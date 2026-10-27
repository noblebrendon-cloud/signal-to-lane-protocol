"""Behavioral checks for the proposed cross-format evidence contract."""
import copy
import json
import unittest
from pathlib import Path

from validate import GATES, PROFILES, approval_subject, attempt_key, validate

FIXTURES = Path(__file__).parent / "fixtures"


def fixture(kind="merchandise"):
    return json.loads((FIXTURES / f"synthetic-{kind}.json").read_text())


class ReferenceCaseTests(unittest.TestCase):
    def test_same_contract_accepts_all_three_synthetic_formats(self):
        for kind in PROFILES:
            with self.subTest(kind=kind):
                self.assertEqual(validate(fixture(kind)), [])

    def test_historical_success_does_not_fabricate_missing_evidence(self):
        record = json.loads((FIXTURES / "historical-merchandise.json").read_text())
        errors = validate(record)
        self.assertIn("asset digest missing or invalid", errors)
        self.assertIn("publication not verified", errors)
        self.assertEqual(record["approvals"], [])

    def test_each_human_gate_is_required_for_every_format(self):
        for kind in PROFILES:
            for gate in GATES:
                with self.subTest(kind=kind, gate=gate):
                    record = fixture(kind)
                    record["approvals"] = [a for a in record["approvals"] if a["gate"] != gate]
                    self.assertIn(f"{gate}: explicit human approval required", validate(record))

    def test_latest_revocation_overrides_prior_approval(self):
        record = fixture()
        record["approvals"].append({**record["approvals"][-1], "decision": "revoked"})
        self.assertIn("publication: explicit human approval required", validate(record))

    def test_asset_change_invalidates_approval_in_every_format(self):
        for kind in PROFILES:
            with self.subTest(kind=kind):
                record = fixture(kind)
                record["asset"]["sha256"] = "b" * 64
                self.assertIn("production: stale or missing approval binding", validate(record))
                self.assertIn("publication: stale or missing approval binding", validate(record))

    def test_copy_destination_account_visibility_changes_need_reapproval(self):
        for section, key in [("packet", "copy"), ("target", "destination"), ("target", "account"), ("target", "visibility")]:
            with self.subTest(section=section, key=key):
                record = fixture()
                record[section][key] = "changed-after-approval"
                self.assertIn("publication: stale or missing approval binding", validate(record))

    def test_missing_provenance_holds(self):
        record = fixture()
        record["asset"]["source_refs"] = []
        self.assertIn("asset source chain required", validate(record))

    def test_type_specific_preflight_cannot_be_skipped(self):
        for kind, checks in PROFILES.items():
            with self.subTest(kind=kind):
                record = fixture(kind)
                record["preflight"]["checks"][checks[0]] = False
                self.assertIn(f"preflight.{checks[0]}: review required", validate(record))

    def test_export_or_product_creation_is_not_publication(self):
        record = fixture()
        record["publication"]["status"] = "staged"
        self.assertIn("publication not verified", validate(record))

    def test_receipt_must_match_approved_asset_and_target(self):
        for key, value in [("asset_sha256", "c" * 64), ("target", {"visibility": "unlisted"}), ("remote_id", "different-product")]:
            with self.subTest(key=key):
                record = fixture()
                record["publication"][key] = value
                self.assertTrue(validate(record))

    def test_receipt_is_required_even_after_success_response(self):
        record = fixture()
        record["publication"]["receipt_ref"] = None
        self.assertIn("publication.receipt_ref: evidence required", validate(record))

    def test_unknown_outcome_blocks_blind_retry(self):
        record = fixture()
        record["attempts"][0]["outcome"] = "unknown"
        self.assertIn("unknown external outcome: reconcile before retry", validate(record))

    def test_lost_response_can_be_reconciled_without_uploading_again(self):
        record = fixture()
        record["attempts"][0]["outcome"] = "unknown"
        record["reconciliations"] = [{"attempt_id": "fixture-attempt-1", "outcome": "found", "remote_id": "fixture-remote-merchandise", "actor": "SIMULATED_OPERATOR", "at": "2026-10-27T10:27:00Z", "evidence_ref": "fixture:remote-lookup"}]
        self.assertEqual(validate(record), [])

    def test_retry_requires_reconciliation_and_operator_decision(self):
        record = fixture()
        first = copy.deepcopy(record["attempts"][0])
        first.update(outcome="failed", error="Simulated generic vendor error", reconciliation_ref="fixture:confirmed-absent", at="2026-10-27T10:22:00Z")
        record["attempts"][0].update(id="fixture-attempt-2", retry_approval_ref="fixture:human-retry-decision")
        record["attempts"].insert(0, first)
        self.assertEqual(validate(record), [])
        del record["attempts"][1]["retry_approval_ref"]
        self.assertIn("retry requires explicit operator decision", validate(record))

    def test_unknown_then_absent_allows_only_later_approved_retry(self):
        record = fixture()
        first = copy.deepcopy(record["attempts"][0])
        first.update(outcome="unknown", at="2026-10-27T10:21:00Z")
        record["attempts"][0].update(id="fixture-attempt-2", retry_approval_ref="fixture:human-retry-decision")
        record["attempts"].insert(0, first)
        record["reconciliations"] = [{"attempt_id":"fixture-attempt-1", "outcome":"absent", "actor":"SIMULATED_OPERATOR", "at":"2026-10-27T10:23:00Z", "evidence_ref":"fixture:remote-absent"}]
        self.assertEqual(validate(record), [])
        record["reconciliations"][0]["at"] = "2026-10-27T10:29:00Z"
        self.assertIn("retry precedes reconciliation", validate(record))

    def test_duplicate_external_success_is_not_hidden(self):
        record = fixture()
        record["attempts"].append({**record["attempts"][0], "id":"fixture-attempt-2", "remote_id":"accidental-duplicate", "retry_approval_ref":"fixture:bad-retry"})
        self.assertIn("exactly one reconciled successful publication required per target/version", validate(record))

    def test_partial_failure_keeps_target_results_separate(self):
        public_store = fixture()
        other_target = fixture("video")
        other_target["publication"]["status"] = "failed"
        self.assertEqual(validate(public_store), [])
        self.assertIn("publication not verified", validate(other_target))

    def test_version_ancestry_and_content_binding_are_required(self):
        record = fixture()
        record["version_history"][0]["supersedes"] = 9
        self.assertIn("broken version ancestry", validate(record))
        record = fixture()
        record["release"]["version"] = 2
        self.assertIn("current version mismatch", validate(record))

    def test_approval_cannot_be_backfilled_after_publication(self):
        record = fixture()
        record["approvals"][-1]["at"] = "2026-10-27T11:00:00Z"
        self.assertIn("publication attempted before approval", validate(record))

    def test_lane_promotion_requires_post_test_evidence_and_human_decision(self):
        record = fixture()
        record["routing"] = {"status":"routed", "lane":"existing-lane", "actor":"SIMULATED_OPERATOR", "at":"2026-11-03T12:00:00Z", "reason":"Reviewed the test; preserve its meaning", "evidence_ref":"fixture:routing-decision"}
        self.assertIn("routing requires post-test evidence", validate(record))
        record["observation"].update(status="recorded", evidence_refs=["fixture:post-test-observation"])
        self.assertEqual(validate(record), [])

    def test_missing_actor_and_timestamps_are_not_approvals(self):
        record = fixture()
        record["approvals"][-1].update(actor=None, at=None)
        self.assertIn("publication: approver and decision evidence required", validate(record))
        self.assertIn("publication: decision timestamp required", validate(record))

    def test_wrong_attempt_snapshot_is_rejected(self):
        record = fixture()
        record["attempts"][0]["subject_sha256"] = "0" * 64
        self.assertIn("attempt does not identify approved snapshot", validate(record))

    def test_malformed_record_is_held(self):
        self.assertTrue(validate(None))
        self.assertTrue(validate({}))


if __name__ == "__main__":
    unittest.main()
