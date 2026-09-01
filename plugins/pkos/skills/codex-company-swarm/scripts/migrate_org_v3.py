#!/usr/bin/env python3
"""Build a non-destructive org-v3 to org-v4 migration plan; never invent new packets."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any, Dict, Iterable

def build(source:Dict[str,Any])->Dict[str,Any]:
    if source.get("schema")!="pkos-company-swarm/org-v3": raise ValueError("source must be org-v3")
    sessions=source.get("sessions",[])
    developers=[s for s in sessions if s.get("role")=="domain-developer"]
    testers=[s for s in sessions if s.get("role")=="quality-engineer"]
    reusable=[{"session_id":s.get("session_id"),"threadId":s.get("threadId"),"affinity":s.get("lane"),"role":s.get("role")} for s in developers[:3]]
    if testers: reusable.append({"session_id":testers[0].get("session_id"),"threadId":testers[0].get("threadId"),"affinity":"shared-test","role":"quality-engineer","rename_to":"T-SHARED-01"})
    archive=[s.get("session_id") for s in sessions if s.get("role") in {"integration-owner","review-chair"} or (s.get("role")=="quality-engineer" and s is not testers[0])]
    pending=[s.get("session_id") for s in sessions if s.get("state") in {"registered","queued","active","attention"} and s.get("session_id")!="TD-01"]
    return {"schema":"pkos-company-swarm/org-v3-to-v4-migration-v1","run_id":source.get("run_id"),"source_schema":"pkos-company-swarm/org-v3","target_schema":"pkos-company-swarm/org-v4","migration_status":"REPACK_REQUIRED" if pending else "READY","preserve":{"evidence":True,"receipts":True,"checkpoints":True,"generation":source.get("generation"),"director_epoch":source.get("director_epoch")},"authority_changes":{"planner":"TD-01","integration_owner":"TD-01","notion_writer":"PK-01-at-gates-only"},"reusable_visible_tasks":reusable,"archive_from_active_registry":archive,"packets_requiring_v3_reissue":pending,"required_steps":["freeze old dispatch","checkpoint org-v3","retain settled evidence","bind TD-01 as integrator","collapse testers to one shared task","archive INT-01 and idle governance roles","reissue pending work as <=1200-character task-packet-v3","validate org-v4 before resume"],"warning":"旧 packet 仅作证据；不得直接 dispatch，也不得虚构缺失的功能 ID、冻结需求、owned scope 或基础 SHA。"}

def main(argv:Iterable[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("source",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args(list(argv) if argv is not None else None)
    try: result=build(json.loads(a.source.read_text(encoding="utf-8")))
    except (OSError,json.JSONDecodeError,ValueError) as exc: print(f"Migration failed: {exc}"); return 1
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"WROTE: {a.output}"); return 0
if __name__=="__main__": raise SystemExit(main())
