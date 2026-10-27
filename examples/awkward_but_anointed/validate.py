"""Offline reference-record checks. Never generates, approves, or publishes an asset."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

PROFILES = {
    "merchandise": ("print_dimensions", "variant_mapping", "mockup_review"),
    "pdf": ("page_render_review", "text_and_links", "accessibility_review"),
    "video": ("playback_review", "audio_and_rights", "captions_and_framing"),
}
GATES = ("campaign", "production", "publication")


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def approval_subject(record, gate):
    """Bind approval to the full relevant snapshot, including copy and target."""
    keys = ["campaign"]
    if gate != "campaign":
        keys += ["release", "asset", "packet", "target", "version_history"]
    if gate == "publication":
        keys += ["preflight"]
    return digest({key: record.get(key) for key in keys})


def attempt_key(record):
    return digest({"release": record.get("release"), "target": record.get("target")})


def _time(value):
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if dt.tzinfo is not None else None
    except (AttributeError, ValueError, TypeError):
        return None


def validate(record):
    """Return reasons to hold. This checks assertions, not their external truth."""
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def fields(value, names, label):
        require(isinstance(value, dict), f"{label}: object required")
        if not isinstance(value, dict):
            return {}
        for name in names:
            require(bool(value.get(name)), f"{label}.{name}: evidence required")
        return value

    if not isinstance(record, dict):
        return ["record: object required"]
    require(record.get("schema") == "release-reference-v1", "unsupported schema")
    require(record.get("basis") in {"synthetic", "historical_reconstruction", "observed"}, "basis required")
    fields(record.get("campaign"), ("id", "signal_ref", "purpose", "boundary"), "campaign")
    release = fields(record.get("release"), ("id", "kind", "version"), "release")
    kind = release.get("kind")
    require(kind in PROFILES, "unsupported asset kind")
    asset = fields(record.get("asset"), ("id", "sha256", "source_refs", "transformation", "tool", "rights_review_ref"), "asset")
    require(isinstance(asset.get("source_refs"), list) and bool(asset.get("source_refs")), "asset source chain required")
    require(bool(re.fullmatch(r"[0-9a-f]{64}", str(asset.get("sha256", "")))), "asset digest missing or invalid")
    fields(record.get("packet"), ("title", "copy", "spec_ref"), "packet")
    fields(record.get("target"), ("platform", "account", "destination", "visibility"), "target")
    versions = record.get("version_history", [])
    require(isinstance(versions, list) and bool(versions), "version history required")
    previous = None
    seen_versions = set()
    for version in versions if isinstance(versions, list) else []:
        if not isinstance(version, dict):
            errors.append("invalid version record")
            continue
        number = version.get("version")
        require(isinstance(number, int) and not isinstance(number, bool) and number > 0, "positive integer version required")
        require(number == (previous + 1 if isinstance(previous, int) else 1), "version sequence must start at 1 and increase")
        require(str(number) not in seen_versions, "duplicate version")
        require(version.get("supersedes") == previous, "broken version ancestry")
        require(bool(version.get("change_note")) and bool(version.get("asset_sha256")), "version change evidence required")
        seen_versions.add(str(number))
        previous = number
    if isinstance(versions, list) and versions and isinstance(versions[-1], dict):
        require(versions[-1].get("version") == release.get("version"), "current version mismatch")
        require(versions[-1].get("asset_sha256") == asset.get("sha256"), "current asset differs from version history")

    preflight = fields(record.get("preflight"), ("reviewer", "at", "evidence_ref", "checks"), "preflight")
    require(preflight.get("status") == "passed", "preflight not passed")
    preflight_time = _time(preflight.get("at"))
    require(preflight_time is not None, "preflight timestamp required")
    checks = preflight.get("checks", {})
    for name in PROFILES.get(kind, ()):
        require(isinstance(checks, dict) and checks.get(name) is True, f"preflight.{name}: review required")

    approvals = record.get("approvals", [])
    require(isinstance(approvals, list), "approvals must be a list")
    gate_times = []
    for gate in GATES:
        candidates = [a for a in approvals if isinstance(a, dict) and a.get("gate") == gate] if isinstance(approvals, list) else []
        current = candidates[-1] if candidates else {}
        require(current.get("decision") == "approved", f"{gate}: explicit human approval required")
        require(bool(current.get("actor")) and bool(current.get("evidence_ref")), f"{gate}: approver and decision evidence required")
        require(current.get("subject_sha256") == approval_subject(record, gate), f"{gate}: stale or missing approval binding")
        when = _time(current.get("at"))
        require(when is not None, f"{gate}: decision timestamp required")
        gate_times.append(when)
    if all(gate_times):
        require(gate_times == sorted(gate_times), "approval order invalid")
        if preflight_time:
            require(gate_times[1] <= preflight_time <= gate_times[2], "preflight must follow production approval and precede publication approval")

    attempts = record.get("attempts", [])
    require(isinstance(attempts, list) and bool(attempts), "publication attempt evidence required")
    attempt_ids = set()
    successes = []
    reconciliations = record.get("reconciliations", [])
    require(isinstance(reconciliations, list), "reconciliations must be a list")
    for attempt in attempts if isinstance(attempts, list) else []:
        if not isinstance(attempt, dict):
            errors.append("invalid attempt record")
            continue
        require(isinstance(attempt.get("id"), str) and bool(attempt.get("id")) and str(attempt.get("id")) not in attempt_ids, "unique attempt id required")
        if attempt_ids:
            require(bool(attempt.get("retry_approval_ref")), "retry requires explicit operator decision")
        attempt_ids.add(str(attempt.get("id")))
        require(attempt.get("idempotency_key") == attempt_key(record), "attempt target/version key mismatch")
        require(attempt.get("subject_sha256") == approval_subject(record, "publication"), "attempt does not identify approved snapshot")
        require(bool(attempt.get("evidence_ref")), "attempt receipt or failure evidence required")
        when = _time(attempt.get("at"))
        require(when is not None, "attempt timestamp required")
        if when and gate_times[-1]:
            require(when >= gate_times[-1], "publication attempted before approval")
        outcome = attempt.get("outcome")
        require(outcome in {"failed", "unknown", "succeeded"}, "invalid attempt outcome")
        if outcome == "unknown":
            resolved = [r for r in reconciliations if isinstance(r, dict) and r.get("attempt_id") == attempt.get("id")] if isinstance(reconciliations, list) else []
            if len(resolved) != 1:
                errors.append("unknown external outcome: reconcile before retry")
            else:
                resolution = resolved[0]
                require(resolution.get("outcome") in {"absent", "found"}, "invalid reconciliation outcome")
                require(bool(resolution.get("actor")) and bool(resolution.get("evidence_ref")), "reconciliation actor and evidence required")
                resolved_at = _time(resolution.get("at"))
                require(resolved_at is not None and when is not None and resolved_at >= when, "reconciliation timestamp invalid")
                later = attempts[attempts.index(attempt) + 1:]
                require(all(_time(a.get("at")) and resolved_at and _time(a.get("at")) >= resolved_at for a in later if isinstance(a, dict)), "retry precedes reconciliation")
                if resolution.get("outcome") == "found":
                    require(bool(resolution.get("remote_id")), "reconciliation remote id required")
                    successes.append({**attempt, "remote_id": resolution.get("remote_id"), "at": resolution.get("at")})
        if outcome == "failed":
            require(bool(attempt.get("error")) and bool(attempt.get("reconciliation_ref")), "failed attempt requires error and remote-state reconciliation")
        if outcome == "succeeded":
            require(bool(attempt.get("remote_id")), "successful attempt requires remote id")
            successes.append(attempt)
    require(len(successes) == 1, "exactly one reconciled successful publication required per target/version")

    publication = fields(record.get("publication"), ("receipt_ref", "url", "remote_id", "verified_by", "verified_at"), "publication")
    require(publication.get("status") == "verified", "publication not verified")
    require(publication.get("target") == record.get("target"), "publication target or visibility mismatch")
    require(publication.get("subject_sha256") == approval_subject(record, "publication"), "receipt does not identify approved snapshot")
    require(publication.get("asset_sha256") == asset.get("sha256") and bool(asset.get("sha256")), "receipt asset digest mismatch")
    verified_at = _time(publication.get("verified_at"))
    require(verified_at is not None, "publication verification timestamp required")
    if len(successes) == 1:
        require(publication.get("remote_id") == successes[0].get("remote_id"), "receipt remote id mismatch")
        attempt_at = _time(successes[0].get("at"))
        if verified_at and attempt_at:
            require(verified_at >= attempt_at, "verification precedes publication attempt")

    observation = fields(record.get("observation"), ("status", "review_due"), "observation")
    require(_time(observation.get("review_due")) is not None, "observation review date required")
    require(observation.get("status") in {"pending", "recorded"}, "invalid observation state")
    routing = fields(record.get("routing"), ("status",), "routing")
    require(routing.get("status") in {"pending", "routed", "retired", "archived"}, "invalid routing state")
    if routing.get("status") != "pending":
        require(observation.get("status") == "recorded" and bool(observation.get("evidence_refs")), "routing requires post-test evidence")
        fields(routing, ("actor", "at", "reason", "evidence_ref"), "routing")
        routing_at = _time(routing.get("at"))
        require(routing_at is not None, "routing timestamp required")
        if routing_at and verified_at:
            require(routing_at >= verified_at, "routing precedes verified publication")
        if routing.get("status") == "routed":
            require(bool(routing.get("lane")), "routing lane required")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="A JSON reference record; no external actions occur")
    args = parser.parse_args()
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        errors = validate(record)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors = [f"invalid record: {exc}"]
    print(json.dumps({"result": "hold" if errors else "consistent", "limitations": "Record consistency only; no human identity, media bytes, receipt, or live integration verified.", "reasons": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
