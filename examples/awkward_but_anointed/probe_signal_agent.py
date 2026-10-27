"""Optional offline probes of four pinned Signal Agent source files.

No checkout mutation, credentials, media rendering, vendor requests, or publication.
All state goes in TemporaryDirectory; YouTube calls use an injected fake uploader.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import socket
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

COMMIT = "fb2918bcf4559bdec37b8367ec458dff2528db11"
PINS = {
    "app/letters_of_light/release.py": "ab398468dfdeaff2cbbcc5d1e677004620c02e98",
    "app/letters_of_light/release_site.py": "b679b826c5a1a7c434db3fcce97cd3c9cb72abab",
    "app/letters_of_light/publishers/base.py": "4b4043e613feb8fe56b92cf01f33507e979f8cd5",
    "app/letters_of_light/publishers/youtube.py": "4a2a24c0b2e02c943f7b1660334428e03dfaac27",
}


def load_pinned_modules(source):
    for name, expected in PINS.items():
        data = (source / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if actual != expected:
            raise SystemExit(f"Refusing changed source: {name}. Expected bytes from {COMMIT}.")
    # Avoid executing unrelated package initialization in a supplied checkout.
    sys.dont_write_bytecode = True
    for name in ["app", "app.letters_of_light", "app.letters_of_light.publishers"]:
        module = types.ModuleType(name)
        module.__path__ = [str(source.joinpath(*name.split(".")))]
        sys.modules[name] = module
    return tuple(importlib.import_module(name) for name in [
        "app.letters_of_light.release", "app.letters_of_light.release_site",
        "app.letters_of_light.publishers.youtube",
    ])


class FakeUploader:
    def __init__(self, fail=False):
        self.calls = 0
        self.fail = fail

    def upload(self, **kwargs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("simulated upload failure")
        return {"video_id": "fixture-video-id", "url": "https://example.invalid/video"}


class SourceProbes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = patch.dict(os.environ, {"SIGNAL_AGENT_ROOT": str(self.root)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.letter = self.root / "data/state/letters_of_light/fixture"
        self.letter.mkdir(parents=True)
        (self.letter / "final.mp4").write_bytes(b"SYNTHETIC NON-MEDIA BYTES")
        (self.letter / "visual.png").write_bytes(b"SYNTHETIC NON-IMAGE BYTES")
        self.write("letter.json", {
            "letter_id": "fixture", "lifecycle_state": "registered", "theme": "reference",
            "title": "Synthetic reference", "text": "Synthetic body", "scripture_ref": "",
            "evaluation": {"decision": "accept", "total": 24, "audio_alignment": 4},
            "video_path": str(self.letter / "final.mp4"), "visual_path": str(self.letter / "visual.png"),
        })
        self.write("routing.json", {"youtube": {"title": "Synthetic reference"}})
        self.write("interaction.json", {"questions": ["Synthetic question"]})

    def write(self, name, value):
        (self.letter / name).write_text(json.dumps(value))

    def read(self, name):
        return json.loads((self.letter / name).read_text())

    def export(self):
        release.create_release_candidate("fixture")
        release.approve_release("fixture")
        release.export_campaign("fixture")

    def test_pdf_only_record_is_ineligible(self):
        letter = self.read("letter.json")
        letter["video_path"] = ""
        letter["pdf_path"] = str(self.letter / "document.pdf")
        self.write("letter.json", letter)
        (self.letter / "document.pdf").write_bytes(b"SYNTHETIC PDF BYTES")
        result = release.check_release_eligibility("fixture")
        self.assertFalse(result.eligible)
        self.assertTrue(any("video" in reason for reason in result.reasons))

    def test_export_requires_approval(self):
        release.create_release_candidate("fixture")
        with self.assertRaisesRegex(RuntimeError, "approved"):
            release.export_campaign("fixture")

    def test_approved_export_is_local_and_lacks_actor_or_digest_binding(self):
        self.export()
        data = self.read("release.json")
        self.assertEqual(data["release_state"], "exported")
        self.assertEqual(data["targets"]["youtube"]["status"], "pending")
        event = next(e for e in data["events"] if e["event_type"] == "ReleaseApproved")
        self.assertNotIn("actor", event)
        self.assertNotIn("subject_sha256", event)

    def test_changed_media_can_be_exported_under_old_boolean_approval(self):
        self.export()
        (self.letter / "final.mp4").write_bytes(b"CHANGED SYNTHETIC MEDIA BYTES")
        release.export_campaign("fixture")
        self.assertTrue(self.read("release.json")["approved"])
        self.assertEqual((self.letter / "release_export/final.mp4").read_bytes(), b"CHANGED SYNTHETIC MEDIA BYTES")

    def test_site_published_status_means_local_file_write(self):
        self.export()
        site_root = self.root / "site"
        site_root.mkdir()
        (site_root / "index.html").write_text("<html></html>")
        result = site.publish_release_site("fixture", site_root=str(site_root), base_url="https://example.invalid")
        self.assertTrue(Path(result["page_path"]).is_file())
        self.assertEqual(self.read("release.json")["targets"]["site"]["status"], "published")

    def test_mock_upload_records_id_and_skips_known_duplicate(self):
        self.export()
        uploader = FakeUploader()
        youtube.publish_youtube("fixture", uploader=uploader)
        result = youtube.publish_youtube("fixture", uploader=uploader)
        self.assertTrue(result["skipped"])
        self.assertEqual(uploader.calls, 1)
        self.assertEqual(self.read("release.json")["targets"]["youtube"]["platform_id"], "fixture-video-id")

    def test_mock_failure_records_target_error(self):
        self.export()
        with self.assertRaisesRegex(Exception, "simulated upload failure"):
            youtube.publish_youtube("fixture", uploader=FakeUploader(fail=True))
        self.assertEqual(self.read("release.json")["targets"]["youtube"]["status"], "failed")

    def test_candidate_recreation_resets_target_receipt_fields(self):
        self.export()
        youtube.publish_youtube("fixture", uploader=FakeUploader())
        recreated = release.create_release_candidate("fixture")
        self.assertEqual(recreated["targets"]["youtube"]["status"], "pending")
        self.assertIsNone(recreated["targets"]["youtube"]["platform_id"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Checkout or source slice containing the four pinned files")
    args = parser.parse_args()
    global release, site, youtube
    release, site, youtube = load_pinned_modules(args.source.resolve())
    with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden in reference probe")), patch.object(socket, "create_connection", side_effect=AssertionError("Network forbidden in reference probe")):
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SourceProbes))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
