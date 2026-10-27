# Awkward But Anointed: approved moment to traceable release

Second Signal-to-Lane reference scenario, documented **2026-10-27** from the **2026-10-17** release. Owner: Brendon R. Coleman.

**Finding:** a human-operated Printful-to-Shopify release is supported by the owner's account. A complete, portable audit trail and an automated Signal Agent publication pipeline are not established. This case tests the approval and evidence structure across merchandise, PDFs, and videos without publishing any of them.

This is an additive reference profile, not a new permanent content lane, product launch, publisher integration, or replacement for the protocol. The historical campaign folder and original machine identifiers were not recovered. Names beginning `retrospective-` in the fixture are documentation labels created for this case.

## Contents

- [Historical record and protocol mapping](#workflow-and-protocol-mapping) below.
- [Signal Agent capability review](CAPABILITY_REVIEW.md): source pins, working local behavior, and gaps.
- [Validation contract and runbook](VALIDATION.md): human gates, required records, failure handling, and repeatable checks.
- [Historical merchandise record](fixtures/historical-merchandise.json): incomplete evidence, expected hold.
- Synthetic [merchandise](fixtures/synthetic-merchandise.json), [PDF](fixtures/synthetic-pdf.json), and [video](fixtures/synthetic-video.json) records: identical governing structure, different preflight checks.

## Historical source register

The historical sources below are **reported history**, not new live-platform inspections. Relevant conversation excerpts were retrieved on 2026-10-27. Original screenshots, full transcript, media bytes, vendor responses, and public-post receipts were not recovered into this repository. Their absence here limits independent reproduction of the historical audit; it does not negate the owner's confirmation that the shirt was released. Source times below are the retrieved record's UTC timestamps, not exact action times.

| ID | Source and locator | What it supports | Limit |
| --- | --- | --- | --- |
| H1 | Owner's 2026-10-27 request to add this scenario | Completed October 17 Printful/Shopify shirt release; desired capability applies also to PDFs, videos, and other approved publications | Retrospective attestation, not vendor receipt |
| H2 | “Breakout Video Analysis,” user messages 2026-10-17 13:39:36Z and 13:46:25Z, recovered conversation | A source video reached roughly 24,000 views in a day; an audience comment requested a shirt using “Awkward and Anointed” with “ADHD” | No original post/comment ID or screenshot recovered; the requested wording and final product title differ; no medical claim about the commenter is inferred |
| H3 | Same conversation, user messages and supplied excerpts around the Printful session | User needed an uploadable design, stayed in Printful, saw repeat errors, confirmed both saved attempts survived, said the design looked good, and later reported success | Informal decisions; no complete, timestamped approval of final file, variants, price, or publication target recovered |
| H4 | Same conversation, prior assistant output at 2026-10-17 15:34:34Z | Reported initial 1,254 × 1,254 file warning and revised transparent 4,800 × 4,275 PNG; tracing and Runway 4× upscaling were described | Original bytes, generation job, exact transformation order, rights review, final submitted file identity and hashes unverified; claimed 300-DPI metadata is not proof of print quality |
| H5 | Prior assistant publication/audit reports, 2026-10-17 16:58:03Z, 21:12:12Z and 21:15:05Z | Reported Shopify product ID `9593655460097`, 54 variants, seven mockups, Printful links and Online Store publication | Those inspections were not rerun here; these are reported details, not independently verified current state. No storefront URL, channel receipt, checkout or fulfillment proof recovered |
| H6 | Same conversation, user follow-up excerpts after success | Intent to reply with the link and circulate the video on other platforms; later discussion of a sustained source-video baseline | Reply and cross-platform posts lack publication receipts; no shirt sales, click attribution, or campaign-specific conversion evidence |

Only the release-relevant summary is committed. No private screenshots, account credentials, customer information, or unrelated conversation material is needed for the reference test.

## Workflow and protocol mapping

This uses a direct audience request rather than the first reference campaign's TikTok search-gap signal. The protocol already admits recurring comments and high-performing themes as signals. A single request is sufficient to start a bounded experiment; it is not sufficient to establish a permanent lane.

| Actual sequence | Evidence and status | Existing protocol stage / file | Reproducible requirement exposed |
| --- | --- | --- | --- |
| 1. Source video attracts attention; audience asks for a shirt | H2, reported audience signal | Capture signal; `01_search_insights/TREND_NOTES.md`, `08_screenshots/comments/` | Preserve post/comment reference, observation time, relevant excerpt and context. Separate source-video performance from release outcomes |
| 2. User chooses to turn the moment into a shirt | H1–H3; intent demonstrated in conversation, formal campaign record unknown | Temporary campaign and boundaries; `00_campaign_manifest/` | Human approves purpose, exact adapted message, exclusions and allowed release types before production work. Do not invent an original campaign folder |
| 3. Prepare design and copy; address print-resolution warning | H3–H4; revision process reported, byte lineage incomplete | Production packet; `02_content_angles/`, `03_scripts/`, `04_post_queue/` | Record source artwork, revisions, tool/job references, output hash and print dimensions. Review final wording rather than assuming the comment was copied verbatim |
| 4. User reviews the design in Printful and continues description work | H3; informal design acceptance, exact final packet approval not recovered | Ready-to-produce gate in `04_post_queue/READY_TO_RECORD.md` | Explicit production approval must identify final design, mockup, description, variants and commercial settings. Design acceptance alone does not authorize every destination |
| 5. Repeated Printful publishing errors; two attempts remain saved | H3–H5; failures and retained drafts reported; error code and root cause unknown | Existing protocol lacks external-attempt detail; record alongside post queue | Preserve each attempt and draft ID. Inspect destination state before retry; no assumption that a generic error means nothing was created |
| 6. Product published to Shopify | H1 owner-confirmed release; H5 reported product/channel details | Controlled public test; `05_published_posts/PUBLISHED_LOG.md` | Final human approval names account, channel and visibility. Retain provider ID, receipt, public URL and read-back verification; product creation is distinct from channel visibility |
| 7. Reply to the audience and distribute links elsewhere | H6, intended follow-up; completed posts unverified | Posting sequence / published log | Each reply or platform post needs its own approval scope and receipt. Shopify Online Store publication does not prove Buy Button, Facebook, Instagram or TikTok publication |
| 8. Observe response; decide retention, expansion or retirement | H6, qualitative source-video observation only; permanent routing unverified | `06_performance_notes/` then `07_cross_lane_promotions/ROUTING_LOG.md` | Capture a dated observation window and post/product-specific evidence. Human decides lane routing or archive; no automatic promotion from a view spike |

“Production” here means preparing artwork, product configuration and publication assets. No physical shirt manufacturing, order, delivery, or successful checkout is claimed.

## Retrospective asset and version history

| Documentation label | Known or reported material | Missing evidence |
| --- | --- | --- |
| H-art-early | H4 reports a small file triggering Printful's warning | Original file, hash, creation time, tool identity |
| H-art-revised | H4 reports a transparent 4,800 × 4,275 export and describes tracing/upscaling | Source-to-output chain, generation/export job, rights review, actual print-area suitability |
| H-printful-attempt-A / B | H3 says two saved attempts survived errors | Actual draft/template IDs, timestamps, field differences and submitted file hashes |
| H-shopify-release | H1 confirms release; H5 reports product ID and variant count | Immutable final artwork/spec version and approval record; publish receipt and public-channel read-back |

The two saved Printful attempts are **not assumed to be two artwork versions**. The exact revision chosen for the successful push remains unknown. No candidate IDs, final filenames, file hashes, approvals or precise publish times have been fabricated.

## What this scenario demonstrates

The owner completed a rapid, manually supervised response from audience demand to a merchandise listing. It also exposed real failure recovery: retained drafts survived repeated errors. The broader “approved moment → finished, traceable release” capability remains a requirement, not an accomplished integration.

The synthetic PDF and video records are **proposed counterfactual exercises** using the same campaign purpose. They are not historical October 17 releases, actual media, or approved publication instructions. The offline checker tests record consistency; humans still need to review the actual asset and inspect the destination before claiming a real release.

The historical record intentionally fails the stronger completeness check. Recovering missing evidence later should add a dated correction or new evidence record with its source and confidence; it must never turn a retrospective reconstruction into a backdated approval.

Related feedback: [Signal-to-Lane issue #1](https://github.com/noblebrendon-cloud/signal-to-lane-protocol/issues/1). This scenario answers its request for additional campaign examples. It does not close that general feedback issue.
