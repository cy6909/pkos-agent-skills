#!/usr/bin/env python3
"""Validate a product-delivery-first Company Swarm v0.10 organization manifest."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

SCHEMA="pkos-company-swarm/org-v4"; MODE="acceptable-product-per-token"
STATES={"registered","queued","active","attention","settled","archived"}
PRODUCT="domain-developer"; NON_PRODUCT={"quality-engineer","review-chair","coordination-governance-scribe","ci-engineer","verifier"}
WRITERS={"domain-developer","quality-engineer","ci-engineer"}
PACKET_KEYS={"feature_id","frozen_requirements","owned_files_modules","base_sha","acceptance_criteria","prohibitions","notion_links"}
NOTION_GATES=["requirements_frozen","lane_handoff","candidate_frozen","strict_review_terminal","deployment_acceptance_terminal"]
FEATURE_FIELDS=["development_session","test_session","review_integration_session","round_result","accepted_candidate","acceptance_method","evidence_and_gaps","next_action"]
PROGRESS_FIELDS=["accepted_feature_delta","candidate_sha","passed_real_gates","p0_p1_blockers","productive_code_outputs","token_direction"]

def nonempty(v:Any)->bool: return isinstance(v,str) and bool(v.strip())
def merge(a:Dict[str,Any],b:Dict[str,Any])->None:
    for k,v in b.items():
        if isinstance(v,dict) and isinstance(a.get(k),dict): merge(a[k],v)
        else: a[k]=v
def load_json(path:Path)->Dict[str,Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value,dict): raise ValueError("organization manifest must be an object")
    if nonempty(value.get("$extends")):
        base=load_json(path.parent/value["$extends"]); removed=set(value.get("remove_sessions",[]))
        base["sessions"]=[x for x in base.get("sessions",[]) if x.get("session_id") not in removed]
        merge(base,value.get("patch",{}))
        for sid,patch in value.get("session_patches",{}).items():
            target=next((x for x in base.get("sessions",[]) if x.get("session_id")==sid),None)
            if target is None: raise ValueError(f"session patch target not found: {sid}")
            merge(target,patch)
        base.setdefault("sessions",[]).extend(value.get("add_sessions",[])); value=base
    return value
def prefix(v:str)->str:
    t=v.strip().replace("\\","/"); pos=[t.find(x) for x in ("*","?","[") if t.find(x)>=0]
    return t[:min(pos or [len(t)])].rstrip("/")
def overlaps(a:str,b:str)->bool:
    a,b=prefix(a),prefix(b); return bool(a and b and (a==b or a.startswith(b+"/") or b.startswith(a+"/")))

def validate_packet(s:Dict[str,Any],errors:List[str])->None:
    sid=s.get("session_id","?"); p=s.get("task_packet")
    if not isinstance(p,dict): errors.append(f"{sid} task_packet must be an object"); return
    if set(p)!=PACKET_KEYS: errors.append(f"{sid} task_packet must contain only the seven allowed fields; repeated context is forbidden")
    if not nonempty(p.get("feature_id")): errors.append(f"{sid} task requires a feature_id")
    if s.get("role") in WRITERS and not any(nonempty(x) for x in p.get("owned_files_modules",[]) if isinstance(x,str)): errors.append(f"writer {sid} requires owned scope")
    if not nonempty(p.get("base_sha")): errors.append(f"{sid} requires exact base_sha")
    size=len(json.dumps(p,ensure_ascii=False,separators=(",",":")))
    if size>1200: errors.append(f"{sid} task_packet exceeds 1200 Chinese characters ({size})")
    settlement=s.get("settlement","")
    if not isinstance(settlement,str) or len(settlement)>600: errors.append(f"{sid} settlement exceeds 600 Chinese characters")
    if s.get("state")=="settled" and not s.get("settlement_artifact_refs"): errors.append(f"{sid} settled task requires evidence links")

def validate(data:Dict[str,Any])->List[str]:
    e:List[str]=[]
    if data.get("schema")!=SCHEMA: return [f"schema must be {SCHEMA}; migrate legacy org-v3 before dispatch"]
    if data.get("mode")!=MODE: e.append(f"mode must be {MODE}")
    if data.get("root_session_id")!="TD-01" or data.get("spawn_authority")!=["TD-01"] or data.get("integration_owner_session_id")!="TD-01": e.append("TD-01 must be sole planner/spawner and cumulative integrator")
    budget=data.get("staffing_budget",{}); expected={"max_product_lanes":3,"hard_cap_active_child_tasks":6,"max_registered_visible_tasks_per_run":8,"min_product_code_share_percent":70}
    for k,v in expected.items():
        if budget.get(k)!=v: e.append(f"staffing_budget.{k} must be {v}")
    sessions=data.get("sessions",[])
    if not isinstance(sessions,list) or not sessions: return e+["sessions must be a non-empty array"]
    if len(sessions)>8: e.append("registered visible task hard cap is 8")
    by:Dict[str,Dict[str,Any]]={}; roles:Dict[str,int]={}; notion=[]; scopes:List[Tuple[str,str]]=[]
    for s in sessions:
        sid,role=s.get("session_id"),s.get("role")
        if not nonempty(sid) or sid in by: e.append("session IDs must be unique and non-empty"); continue
        by[sid]=s; roles[role]=roles.get(role,0)+1
        if s.get("visible_task") is not True or s.get("transport")!="visible_codex_task": e.append(f"{sid} must be sidebar-visible; hidden subagents are forbidden")
        for f in ("threadId","hostId","title","model","reasoning_effort","model_rationale","risk_level","routing_source","lane"):
            if not nonempty(s.get(f)): e.append(f"{sid}.{f} must be non-empty")
        if s.get("state") not in STATES: e.append(f"{sid} state is invalid")
        if sid=="TD-01":
            if role!="technical-director" or s.get("root_task") is not True or s.get("integration_owner") is not True or s.get("created_via")!="current_task": e.append("TD-01 must be current planner and integration owner")
        elif s.get("may_delegate") is not False or s.get("created_via")!="create_thread" or s.get("parent_session_id")!="TD-01": e.append(f"{sid} must use create_thread and may_delegate=false")
        if role=="integration-owner": e.append("separate integration-owner task is forbidden")
        if role in WRITERS and not nonempty(s.get("worktree")): e.append(f"repository writer {sid} requires isolated worktree")
        if s.get("notion_write") is True: notion.append(sid)
        validate_packet(s,e)
        if s.get("state")=="active" and s.get("activity_kind") in {"waiting","status_report","context_reload","environment_blocked"} and s.get("productive") is True: e.append(f"{sid} waiting/report/context/environment work is not productive")
        if s.get("state")=="active" and role in WRITERS:
            scopes += [(sid,x) for x in s.get("task_packet",{}).get("owned_files_modules",[]) if nonempty(x)]
    for i,(a,sa) in enumerate(scopes):
        for b,sb in scopes[i+1:]:
            if a!=b and overlaps(sa,sb): e.append(f"shared ownership must be adjudicated before dispatch: {a}/{b}")
    if roles.get("technical-director")!=1: e.append("exactly one technical-director is required")
    if roles.get(PRODUCT,0)>3 or roles.get("quality-engineer",0)>1 or roles.get("review-chair",0)>1 or roles.get("coordination-governance-scribe",0)>1: e.append("role budget exceeds three developers, one shared tester, one reviewer, or one scribe")
    if notion not in ([],["PK-01"]): e.append("only PK-01 may write Notion")
    active=[s for s in sessions if s.get("session_id")!="TD-01" and s.get("state")=="active"]
    productive=[s for s in active if s.get("productive") is True]
    product=[s for s in productive if s.get("role")==PRODUCT and s.get("activity_kind")=="product_code"]
    share=100 if not productive else round(len(product)*100/len(productive),2)
    concurrency=data.get("concurrency_state",{}); derived={"registered_count":len(sessions),"active_child_count":len(active),"productive_count":len(productive),"product_code_count":len(product),"product_code_share_percent":share}
    for k,v in derived.items():
        if concurrency.get(k)!=v: e.append(f"concurrency_state.{k} must equal {v}")
    if len(active)>6: e.append("active child hard cap is 6")
    if data.get("token_control",{}).get("mode")=="NORMAL" and productive and share<70: e.append("at least 70% of productive concurrency must implement product code")
    if sum(s.get("role") in NON_PRODUCT for s in active)>len(product): e.append("active non-product roles cannot exceed active product developers")
    if len(active)>=4 and len(productive)<3 and concurrency.get("waiting_sessions_reclaimed") is not True: e.append("many active but fewer than three productive sessions requires reclamation")
    lanes=data.get("lanes",[])
    if not isinstance(lanes,list) or len(lanes)>3: e.append("at most three product lanes are allowed"); lanes=[]
    devs:Set[str]=set()
    for lane in lanes:
        fid,did=lane.get("feature_id"),lane.get("developer_session_id")
        if not nonempty(fid): e.append("every lane requires feature_id")
        if did in devs or by.get(did,{}).get("role")!=PRODUCT: e.append("each lane requires one unique product developer")
        devs.add(did)
        if lane.get("tester_session_id")!="T-SHARED-01": e.append("all lanes must use T-SHARED-01")
        if lane.get("handoff_state") in {"READY_FOR_TEST","IN_TEST","TESTED"}:
            checks=lane.get("developer_self_test",{})
            for k in ("push_sha","remote12_clean_checkout","directed_tests","typecheck_build"):
                if not checks.get(k): e.append(f"developer self-test incomplete before tester handoff: {fid}.{k}")
            if lane.get("web") is True:
                b=checks.get("browser",{})
                if b.get("identity")!="cy6909" or b.get("scope")!="public_production" or b.get("status")!="PASS": e.append("web handoff requires public production cy6909 Chrome self-test")
    candidate=data.get("cumulative_candidate",{})
    if candidate.get("maintained_by")!="TD-01" or candidate.get("parallel_candidate_count")!=0 or not nonempty(candidate.get("sha")): e.append("exactly one cumulative candidate maintained by TD-01 is required")
    if data.get("current_gate") in {"G4","G5"} and candidate.get("state") not in {"FROZEN","ACCEPTED"}: e.append("G4/G5 requires one frozen cumulative candidate")
    reviewer=next((s for s in sessions if s.get("role")=="review-chair" and s.get("state")=="active"),None)
    if reviewer and (candidate.get("state")!="FROZEN" or data.get("review_control",{}).get("trigger") not in {"high_risk","abnormal_behavior","strict_acceptance_required"}): e.append("reviewer may start only after candidate freeze with allowed trigger")
    token=data.get("token_control",{}); total,coord=token.get("estimated_total_tokens",0),token.get("estimated_coordination_tokens",0); ratio=0 if not total else coord/total
    if token.get("task_packet_max_chars")!=1200 or token.get("settlement_max_chars")!=600 or token.get("coordination_ratio_limit")!=0.30: e.append("token limits must be packet=1200, settlement=600, coordination=30%")
    consolidate=ratio>0.30 or token.get("minutes_since_candidate",0)>=120 or token.get("minutes_since_accepted_feature",0)>=120 or candidate.get("strict_review_returns",0)>=2
    if consolidate and (token.get("mode")!="CONSOLIDATION_MODE" or token.get("new_task_creation_allowed") is not False): e.append("threshold requires CONSOLIDATION_MODE and no new tasks")
    ci=data.get("ci_control",{}); pre=ci.get("preflight",{}); passed=all(pre.get(k)=="PASS" for k in ("controller","executor","credentials","job_creation","artifact_space")); stopped=ci.get("consecutive_failures",0)>=2 or ci.get("blocked_minutes",0)>15
    if ci.get("lane_state")=="RUNNING" and (not passed or ci.get("preflight_duration_minutes",99)>10): e.append("CI cannot run before <=10 minute successful preflight")
    report=ci.get("stop_report",{})
    if stopped and (ci.get("lane_state")!="STOPPED" or not all(report.get(k) for k in ("blocker","reason","required_authority","recovery_steps")) or report.get("capacity_released_to")!="product_development"): e.append("CI Stop Rule requires STOPPED lane, exact blocker/authority/recovery, and released product capacity")
    notion_cfg=data.get("notion_batching",{})
    if notion_cfg.get("language")!="zh-CN" or notion_cfg.get("write_points")!=NOTION_GATES or notion_cfg.get("micro_event_writes") is not False or notion_cfg.get("target_registry")!="original_product_feature_registry" or notion_cfg.get("duplicate_summary_database") is not False or notion_cfg.get("feature_row_fields")!=FEATURE_FIELDS: e.append("Notion must batch Chinese writeback at five gates into original Feature Registry")
    if by.get("PK-01",{}).get("state")=="active" and notion_cfg.get("active_write_point") not in NOTION_GATES: e.append("PK-01 may work only during gate batch")
    env=data.get("environment_policy",{})
    if env.get("local_allowed")!=["edit","static_git","scheduling"] or env.get("resource_environment")!="remote-12" or env.get("web_acceptance")!="public_production_only" or env.get("identity")!="cy6909" or env.get("github_actions")!="FORBIDDEN" or env.get("private_origin_on_local") is not False: e.append("environment policy must enforce local orchestration, remote-12, public production/cy6909, and no GitHub Actions/private origin")
    progress=data.get("progress_report",{})
    if progress.get("interval_minutes")!=60 or progress.get("fields")!=PROGRESS_FIELDS: e.append("progress report must be a 60-minute delta with the six allowed outcome fields")
    for k in ("accepted_feature_count","candidate_formation_minutes","tokens_per_accepted_feature","coordination_token_ratio","strict_review_returns","real_browser_acceptance_rate"):
        if not isinstance(data.get("delivery_metrics",{}).get(k),(int,float)): e.append(f"delivery_metrics.{k} is required")
    return e

def main(argv:Iterable[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("manifest",type=Path); args=p.parse_args(list(argv) if argv is not None else None)
    try: data=load_json(args.manifest)
    except ValueError as exc: print(f"Company Swarm organization validation failed:\n- {exc}",file=sys.stderr); return 1
    errors=validate(data)
    if errors:
        print("Company Swarm organization validation failed:",file=sys.stderr)
        for x in errors: print(f"- {x}",file=sys.stderr)
        return 1
    print(f"Company Swarm org-v4 validation OK: {len(data['sessions'])} visible tasks, {len(data.get('lanes',[]))} product lanes, one cumulative candidate."); return 0
if __name__=="__main__": raise SystemExit(main())
