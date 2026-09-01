from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
EXAMPLES = ROOT / "assets" / "examples"


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


COORD = load_module("test_coordination", SCRIPTS / "validate_coordination.py")
EVENTS = load_module("test_event_ledger", SCRIPTS / "validate_event_ledger.py")
SCHEMA = load_module("test_notion_schema", SCRIPTS / "validate_notion_schema.py")
SYNC = load_module("test_notion_sync", SCRIPTS / "validate_notion_sync.py")
PACK = load_module("test_pack_delta", SCRIPTS / "validate_pack_delta.py")
TRACE = load_module("test_traceability", SCRIPTS / "validate_traceability.py")
CHECKPOINT = load_module("test_checkpoint", SCRIPTS / "validate_checkpoint.py")
BUNDLE = load_module("test_bundle", SCRIPTS / "validate_coordination_bundle.py")
RESUME = load_module("test_resume", SCRIPTS / "build_resume_plan.py")
ORG_V4 = load_module("test_org_v4", SCRIPTS / "validate_org.py")
MIGRATE = load_module("test_org_migration", SCRIPTS / "migrate_org_v3.py")


class OrganizationV4NotionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("organization.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], ORG_V4.validate(self.data))

    def test_pk01_is_gate_only(self) -> None:
        pk = next(item for item in self.data["sessions"] if item["session_id"] == "PK-01")
        pk["state"] = "active"
        self.assertTrue(any("gate" in item for item in ORG_V4.validate(self.data)))

    def test_rejects_second_notion_writer(self) -> None:
        next(item for item in self.data["sessions"] if item["session_id"] == "D-FE-01")["notion_write"] = True
        self.assertTrue(any("only PK-01" in item for item in ORG_V4.validate(self.data)))

    def test_rejects_micro_event_writes(self) -> None:
        self.data["notion_batching"]["micro_event_writes"] = True
        self.assertTrue(any("five gates" in item for item in ORG_V4.validate(self.data)))

    def test_rejects_duplicate_summary_database(self) -> None:
        self.data["notion_batching"]["duplicate_summary_database"] = True
        self.assertTrue(any("original Feature Registry" in item for item in ORG_V4.validate(self.data)))

    def test_legacy_run_requires_repack(self) -> None:
        plan = MIGRATE.build(example("organization-v3-legacy.example.json"))
        self.assertEqual("REPACK_REQUIRED", plan["migration_status"])
        self.assertEqual("TD-01", plan["authority_changes"]["integration_owner"])
        self.assertIn("INT-01", plan["archive_from_active_registry"])


class CoordinationStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("coordination-state.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], COORD.validate(self.data))

    def test_rejects_stale_director_epoch(self) -> None:
        self.data["sessions"][1]["director_epoch"] = 1
        self.assertTrue(any("stale director_epoch" in item for item in COORD.validate(self.data)))

    def test_rejects_stale_pack(self) -> None:
        self.data["lanes"][0]["pack_revision"] = "pack-1"
        self.assertTrue(any("pack_revision" in item for item in COORD.validate(self.data)))

    def test_rejects_missing_pack_ack(self) -> None:
        self.data["shared_pack"]["acknowledgements"] = self.data["shared_pack"]["acknowledgements"][:-1]
        self.assertTrue(any("missing mandatory" in item for item in COORD.validate(self.data)))

    def test_rejects_accepted_pending_outbox(self) -> None:
        self.data["pending_outbox_count"] = 1
        self.data["notion"]["sync_status"] = "PENDING"
        self.assertTrue(any("ACCEPTED requires" in item for item in COORD.validate(self.data)))

    def test_rejects_in_sync_watermark_gap(self) -> None:
        self.data["notion"]["last_synced_event_seq"] = 16
        self.assertTrue(any("IN_SYNC requires" in item for item in COORD.validate(self.data)))


class EventLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("event-ledger.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], EVENTS.validate(self.data))

    def test_rejects_duplicate_idempotency_key(self) -> None:
        self.data["events"][1]["idempotency_key"] = self.data["events"][0]["idempotency_key"]
        self.assertTrue(any("duplicate idempotency_key" in item for item in EVENTS.validate(self.data)))

    def test_rejects_sequence_gap(self) -> None:
        self.data["events"][4]["seq"] = 7
        self.assertTrue(any("contiguous" in item for item in EVENTS.validate(self.data)))

    def test_rejects_epoch_change_without_takeover(self) -> None:
        self.data["events"][11]["director_epoch"] = 2
        self.assertTrue(any("without TAKEOVER" in item for item in EVENTS.validate(self.data)))

    def test_rejects_invalid_takeover(self) -> None:
        takeover = next(item for item in self.data["events"] if item["event_type"] == "TAKEOVER")
        takeover["payload"]["new_epoch"] = 4
        self.assertTrue(any("consecutive" in item for item in EVENTS.validate(self.data)))

    def test_rejects_unconfirmed_acceptance(self) -> None:
        event = self.data["events"][-1]
        event["notion_sync"] = {"status": "PENDING", "receipt_id": None, "synced_at": None}
        self.assertTrue(any("RUN_ACCEPTED must be confirmed" in item for item in EVENTS.validate(self.data)))


class NotionSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("notion-schema.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], SCHEMA.validate(self.data))

    def test_rejects_missing_database(self) -> None:
        self.data["databases"] = self.data["databases"][:-1]
        self.assertTrue(any("missing required" in item for item in SCHEMA.validate(self.data)))

    def test_rejects_missing_property(self) -> None:
        del self.data["databases"][0]["properties"]["Resume Token"]
        self.assertTrue(any("missing properties" in item for item in SCHEMA.validate(self.data)))


class NotionSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("notion-sync.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], SYNC.validate(self.data))

    def test_rejects_missing_receipt(self) -> None:
        self.data["receipts"] = self.data["receipts"][:-1]
        self.assertTrue(any("requires a receipt" in item or "orphan" in item for item in SYNC.validate(self.data)))

    def test_rejects_watermark_gap(self) -> None:
        self.data["outbox"][5]["status"] = "PENDING"
        self.data["outbox"][5]["receipt_id"] = None
        self.data["receipts"] = [item for item in self.data["receipts"] if item["event_id"] != "EV-006"]
        self.assertTrue(any("watermark_event_seq" in item for item in SYNC.validate(self.data)))

    def test_rejects_duplicate_key(self) -> None:
        self.data["outbox"][1]["idempotency_key"] = self.data["outbox"][0]["idempotency_key"]
        self.assertTrue(any("duplicate outbox idempotency_key" in item for item in SYNC.validate(self.data)))


class PackDeltaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("pack-delta.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], PACK.validate(self.data))

    def test_rejects_missing_ack(self) -> None:
        self.data["acknowledgements"] = self.data["acknowledgements"][:-1]
        self.assertTrue(any("missing acknowledgements" in item for item in PACK.validate(self.data)))

    def test_rejects_high_impact_without_generation_or_compatibility(self) -> None:
        self.data["requires_new_generation"] = False
        self.data["compatibility_preserved"] = False
        self.assertTrue(any("require a new generation" in item for item in PACK.validate(self.data)))


class TraceabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("traceability.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], TRACE.validate(self.data))

    def test_rejects_requirement_without_feature(self) -> None:
        self.data["requirements"][0]["feature_ids"] = []
        self.assertTrue(any("must not be empty" in item for item in TRACE.validate(self.data)))

    def test_rejects_missing_security(self) -> None:
        self.data["features"][0]["test_case_ids"].remove("TC-S-001")
        self.assertTrue(any("lacks Security" in item for item in TRACE.validate(self.data)))

    def test_rejects_missing_performance(self) -> None:
        self.data["features"][0]["test_case_ids"].remove("TC-Q-001")
        self.assertTrue(any("lacks performance" in item for item in TRACE.validate(self.data)))

    def test_rejects_ci_candidate_mismatch(self) -> None:
        self.data["ci_runs"][0]["candidate_commit"] = "wrong"
        self.assertTrue(any("does not test" in item for item in TRACE.validate(self.data)))

    def test_rejects_unconfirmed_writeback(self) -> None:
        self.data["notion_writeback"][0]["status"] = "PENDING"
        self.data["notion_writeback"][0]["evidence_ids"] = []
        self.assertTrue(any("requires confirmed" in item for item in TRACE.validate(self.data)))

    def test_rejects_unreferenced_evidence(self) -> None:
        self.data["evidence"].append({"evidence_id":"E-ORPHAN","type":"DIFF","uri":"git://orphan","checksum":"sha256:"+"d"*64,"produced_by":"D-BE-01","verified_by":"RB-01"})
        self.assertTrue(any("unreferenced evidence" in item for item in TRACE.validate(self.data)))


class CheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = example("checkpoint.example.json")
        self.ledger = example("event-ledger.example.json")

    def test_valid_example(self) -> None:
        self.assertEqual([], CHECKPOINT.validate(self.data, self.ledger))

    def test_rejects_stale_session_epoch(self) -> None:
        self.data["sessions"][0]["director_epoch"] = 1
        self.assertTrue(any("stale director_epoch" in item for item in CHECKPOINT.validate(self.data, self.ledger)))

    def test_rejects_invalid_checksum(self) -> None:
        self.data["artifact_manifest"][0]["checksum"] = "not-a-hash"
        self.assertTrue(any("sha256" in item for item in CHECKPOINT.validate(self.data, self.ledger)))

    def test_rejects_takeover_epoch_mismatch(self) -> None:
        self.data["takeover"]["new_epoch"] = 5
        self.assertTrue(any("consecutive" in item or "match" in item for item in CHECKPOINT.validate(self.data, self.ledger)))


class BundleAndResumeTests(unittest.TestCase):
    def test_valid_bundle(self) -> None:
        self.assertEqual([], BUNDLE.validate_bundle(EXAMPLES / "coordination-bundle"))

    def test_bundle_rejects_run_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dest = Path(temp_dir)
            for source in (EXAMPLES / "coordination-bundle").glob("*.json"):
                (dest / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            state = json.loads((dest / "coordination-state.json").read_text(encoding="utf-8"))
            state["run_id"] = "wrong-run"
            (dest / "coordination-state.json").write_text(json.dumps(state), encoding="utf-8")
            self.assertTrue(any("run_id mismatch" in item for item in BUNDLE.validate_bundle(dest)))

    def test_takeover_resume_plan_increments_epoch_and_reissues(self) -> None:
        plan = RESUME.build(example("checkpoint.example.json"), takeover=True)
        self.assertEqual(3, plan["target_director_epoch"])
        self.assertTrue(plan["takeover_required"])
        self.assertEqual([], plan["reusable_sessions"])
        self.assertGreater(len(plan["sessions_requiring_reissue"]), 0)


if __name__ == "__main__":
    unittest.main()
