# Signal Agent capability review

Inspected on **2026-10-27**. Scope is the supplied GitHub repositories and named Letters of Light paths, not the Windows working tree, all branches, or every Signal Agent subsystem.

- Protocol baseline: [`29ef1e9e88effb861accadb3c395b24f3a7a0b08`](https://github.com/noblebrendon-cloud/signal-to-lane-protocol/tree/29ef1e9e88effb861accadb3c395b24f3a7a0b08).
- Signal Agent baseline: [`fb2918bcf4559bdec37b8367ec458dff2528db11`](https://github.com/noblebrendon-cloud/signal_agent/tree/fb2918bcf4559bdec37b8367ec458dff2528db11), the inspected `main` head. Its commit date is July 4, 2026; do not treat this as a snapshot of October's local studio.
- The recursive Git tree was inspected with `truncated=false`. No `AGENTS.md` appeared in either inspected tree.

## Evidence levels

**Reported history** means the owner or an earlier conversation described an action. **Source-inspected** means code or documentation exists at the pinned revision. **Local-probed** means selected exact source bytes ran against temporary state and synthetic data. **Proposed** means an acceptance requirement in this reference case. None of these alone proves a live external integration.

| Surface | Evidence | Supported behavior | Limit / proposed extension |
| --- | --- | --- | --- |
| Protocol | [Specification](https://github.com/noblebrendon-cloud/signal-to-lane-protocol/blob/29ef1e9e88effb861accadb3c395b24f3a7a0b08/docs/PROTOCOL.md), [generator](https://github.com/noblebrendon-cloud/signal-to-lane-protocol/blob/29ef1e9e88effb861accadb3c395b24f3a7a0b08/tools/New-SignalToLaneCampaign.ps1), [first example](https://github.com/noblebrendon-cloud/signal-to-lane-protocol/blob/29ef1e9e88effb861accadb3c395b24f3a7a0b08/examples/tiktok_religion_debate/README.md); source-inspected | Signal → temporary campaign → packet/test → evidence → lane; reusable folder scaffold | Does not enforce asset-level human approval, byte provenance, vendor retry reconciliation, or per-target publication receipts |
| Merchandise CLI | [`cli.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/cli.py); source-inspected | Declares `merch-candidate` and `merch-approve`; handler calls candidate approval, design generation, spec generation, then prints “Ready for: run_merch_pipeline(spec)” | Candidate approval occurs before design generation; it is not a recorded review of the final artwork. Handler does not call that pipeline. `pipeline.py`, `merch_bridge.py`, `merch_design.py`, and `services/merch_pipeline/` are absent from the inspected tree. The CLI's top-level `pipeline` import fails in the retrieved source slice. No functioning Printful/Shopify bridge demonstrated |
| Candidate/approval/export gate | [`release.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/release.py); source-inspected and local-probed | Eligibility checks registered state, accepted evaluation, score ≥24, audio alignment ≥4, nonempty video/visual files, routing and interaction records. Approval required for export; emits files, manifest and event history | Video-specific requirements reject PDF-only input. Approval records a boolean/time, without reviewer identity or immutable asset/target binding. Nonempty files are not media-quality validation |
| Approval persistence | Same source; local-probed | Rechecks eligibility on export | Changed nonempty media can export under old approval. Recreating a candidate resets target status/IDs even after a mock upload. Proposed profile requires renewed approval and preservation of prior attempt/receipt history |
| Owned-site publisher | [`release_site.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/release_site.py); source-inspected and local-probed | Writes local page, copied media and index; refreshes social exports; records `published` | Module explicitly does not push, deploy or call a platform API. Its local `published` status is not a verified public URL; deployment and public read-back need separate evidence |
| YouTube publisher | [`publishers/youtube.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/publishers/youtube.py), [`base.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/publishers/base.py); source-inspected and local-probed with fake uploader | Real upload implementation exists; requires approval and media, supports visibility, records target IDs/failures and skips a known recorded success unless forced | No credentials or real uploader used here. A returned ID alone does not prove playable/public processing. Visibility is a publish argument, not bound to a signed approval snapshot. Lost-response reconciliation, stronger idempotency and account-specific approval remain acceptance requirements |
| Other social exports | `release.py`; source-inspected | Writes Facebook, Instagram, X and Substack text payloads | Export is not posting. No end-to-end publishing claim is made for those destinations |
| Weekly text workflow | [README](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/docs/letters_of_light/README.md), [`weekly_models.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/weekly_models.py), [`weekly_store.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/weekly_store.py), [`weekly_render.py`](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/app/letters_of_light/weekly_render.py); source-inspected | Separate text-first workflow with content hash, actor-labelled transitions, ledgers, Markdown print packets and a human checklist | Useful precedent; not verified as connected to merchandise/release gates. A Markdown print packet is not a rendered, approved and publicly delivered PDF |

The [root execution map](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/README.md) identifies `signal_agent/` as canonical and cautions against treating other directories as production entrypoints without an explicit designation. This review of `app/letters_of_light/` does not override that boundary.

## Reproduced checks and boundaries

The [optional source probe](probe_signal_agent.py) verifies Git blob hashes for four files before importing them, avoids unrelated package initialization, blocks socket connections, injects a fake YouTube uploader and confines state writes to temporary directories. It uses deliberately invalid media bytes: it proves metadata/file-existence behavior, not rendering, print quality or playback.

Eight probes passed on 2026-10-27:

1. PDF-only record is ineligible under the current video gate.
2. Export without approval is blocked.
3. Approved export remains local and lacks actor/digest-bound approval.
4. Changed media exports under the earlier boolean approval.
5. Site publishing writes local files and sets the local target to `published`.
6. Mock YouTube success records an ID; repeat invocation skips the known success.
7. Mock upload failure records target failure.
8. Candidate recreation clears target receipt fields.

Items 4, 5 and 8 are **observed limitations**, not desired behavior or proposed fixes. The pinned [site tests](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/tests/test_release_site.py), [YouTube tests](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/tests/test_release_youtube.py) and [CLI dispatch tests](https://github.com/noblebrendon-cloud/signal_agent/blob/fb2918bcf4559bdec37b8367ec458dff2528db11/tests/test_letters_of_light_cli_boundary.py) were read, not executed as a complete suite. The dispatch tests mock handlers; they do not establish vendor publication. The runtime here lacked pytest; the added probes and reference checks use only Python's standard library.

## Decision

**Reusable structure: supported by the offline reference exercise. Working shared production/publication pipeline: not established.**

The existing candidate, approval, export, transition-ledger and publisher surfaces are potential attachment points. Connecting them, adding PDF-specific eligibility, hardening identity/version binding, or implementing vendor reconciliation is future work requiring its own scope and tests. This change modifies only the protocol repository's reference material; it does not patch Signal Agent or alter any store, channel, deployment or campaign.
