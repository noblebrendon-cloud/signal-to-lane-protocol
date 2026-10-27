# Reproduce the reference case

This profile asks whether one explicit approval/evidence contract can describe three kinds of release. It does not call Signal Agent commands to approve real work or call any external publisher.

## Required human gates

| Gate | Human reviews | Approval must name | Stop condition |
| --- | --- | --- | --- |
| G1 — campaign | Audience signal, intended meaning, adapted wording, campaign purpose and boundaries | Human actor, decision/time, evidence reference, campaign snapshot | Request is ambiguous, meaning changes without review, or campaign is treated as an automatic permanent lane |
| G2 — production | Final asset and source chain, copy, chosen output type, production specification and intended destination | Release ID/version, source/output SHA-256, reviewed packet, account/channel/visibility and human decision | Missing rights/source evidence; changed design, text, specification or destination; unresolved quality issue |
| G3 — publication | Staged output, completed type-specific preflight, final target/visibility and exact publication copy | Same approved version plus preflight snapshot; a distinct human decision before each target write | Stale approval, wrong account/channel, missing media, failed preflight, unresolved earlier attempt |
| G4 — interpretation/routing | Dated public-test observations, response themes and limits | Human decision to retain, expand, route, retire or archive; reason and evidence; existing lane or explicit proposal for a new lane | Source-video views are substituted for product/PDF/video outcomes, or lane promotion lacks post-test evidence |

One person may perform all gates. The decisions still have different scopes and times. Automated quality checks cannot supply human approval. A design approval is not permission to post anywhere; publication approval for an Online Store listing is not approval for a social reply or a Buy Button channel change.

G1 permits bounded preparation. G2 permits the reviewed production/staging step. G3 permits the named external publication. Ordering in the fixtures is G1 → G2 → staged preflight → G3 → attempt → receipt → observation → G4. A PDF can be rendered for review during preparation; a video can be previewed locally. Those preparations are not public releases.

The checker hashes canonical JSON snapshots using UTF-8, sorted keys, compact separators and unescaped Unicode. G1 binds `campaign`; G2 also binds `release`, `asset`, `packet`, `target`, and `version_history`; G3 additionally binds `preflight`. It compares stored approval hashes; it never creates approval records. The fixture approvals are explicitly simulated. In real use, a human decision record and retained review evidence are required before recording the corresponding digest.

## Minimum evidence record

The JSON format is a **reference-test format**, not a new Signal Agent API or canonical protocol schema. Keep machine data alongside human-readable campaign files.

| Field group | Required evidence | Suggested existing campaign location |
| --- | --- | --- |
| `basis`, source register | Distinguish historical reconstruction, synthetic fixture and directly observed evidence; identify source/time and uncertainty | `00_campaign_manifest/CAMPAIGN_DESCRIPTION.md` |
| `campaign` | Stable ID, original signal reference, purpose and boundary; preserve source post/comment separately from derivative performance | `01_search_insights/TREND_NOTES.md`, `08_screenshots/comments/` |
| `release`, `asset` | ID/type/version; parent source references; creator/tool and transformation record; final output digest; rights-review evidence | `04_post_queue/` with immutable source/output files or controlled references |
| `packet`, `target` | Exact title/copy/spec version; platform, account, destination and visibility; approved commercial or distribution settings | `04_post_queue/READY_TO_RECORD.md` |
| `version_history` | Start at version 1; append revisions with predecessor, change note and output digest; preserve earlier assets, approvals and receipts | `04_post_queue/` plus Git or equivalent append-only history |
| `preflight` | Named reviewer/time, evidence reference and checks for the selected asset type | `04_post_queue/` |
| `approvals` | Separate actor, decision, timestamp, scope digest and retained review evidence for G1/G2/G3; append revocation/reapproval rather than overwriting decisions | `00_campaign_manifest/` and `04_post_queue/` |
| `attempts`, `reconciliations` | Each external attempt ID, exact approved snapshot, target/version key, time, response/error; reconciliation and human retry decision when necessary | `05_published_posts/` |
| `publication` | Provider/object ID, canonical public URL, channel/visibility, submitted asset/version identity, receipt, verifying human and verification time | `05_published_posts/PUBLISHED_LOG.md` |
| `observation`, `routing` | Review date, observation window, distinct source/derivative metrics, qualitative comment themes, human G4 decision and reason | `06_performance_notes/`, `07_cross_lane_promotions/ROUTING_LOG.md` |

A repository can retain the review/receipt itself or a durable controlled reference. Do not commit credentials, private account screens or customer data. A redacted receipt must still identify what was approved or published. Unknown fields stay null; record evidence gaps explicitly. Add later discoveries as dated corrections, not retroactive permission.

Track a separate publication record per destination. Shared assets retain the same lineage; every destination has its own approval scope, attempt key and outcome. The key derived from release identity/version and target is a **local correlation key**. It is not evidence that Printful, Shopify or any other provider supports idempotency keys.

The asset digest records submitted bytes. If a provider transforms media, retain the source-to-submission mapping and any returned derivative/version identifiers. Public verification checks the delivered content and destination; it must not assume that a transcoded video has the same byte hash as the upload.

## Format-specific preflight and publication proof

| Format | Production packet / preflight | Evidence of a completed public test |
| --- | --- | --- |
| Merchandise | Artwork dimensions/transparency and intended print area; final mockup; product/variant mapping, description and approved price/settings; resolve Printful warnings at actual placement size | Printful draft/product reference and submission identity where available; Shopify product ID; exact channel status; storefront URL and dated human read-back showing approved product, variants and visibility. Checkout and physical fulfillment remain separate claims |
| PDF | Source text/version and image/font rights; rendered page review for clipping/order/legibility; text extraction, links and accessibility review; document metadata and final digest | Approved destination/version, upload or deployment receipt, downloadable URL; retrieve and inspect delivered PDF, compare digest where unchanged. Local export or a file on disk is insufficient |
| Video | Source script, footage, narration/music rights and transforms; final playback/audio; captions, framing, duration and target encoding; title/description/thumbnail/visibility | Upload/provider ID, processing result and final visibility; public/playable URL inspected against approved content and account. Upload acceptance, an unlisted URL or a prepared caption alone does not prove the intended public release |

These are proposed acceptance requirements for an operator or future adapter. They do not assert that the historical release retained these records or that any current integration supplies them.

## Failure and recovery requirements

| Failure | Required action and retained evidence | Replay expectation |
| --- | --- | --- |
| Low-resolution or invalid output | Preserve rejected version and warning; correct asset, render/preview again, append version, renew affected approvals | Hold until new preflight and approvals match the actual output |
| Design/spec changed after approval | Retain old version and approvals; append new version with change reason; repeat G2/G3 | Stale digest is rejected |
| Generic vendor error with known absence | Record failed attempt/error, inspect remote state, preserve saved drafts, capture reconciliation; human approves a bounded retry using the same target/version identity | No automatic retry; retry requires decision/evidence |
| Timeout or lost response | Mark outcome unknown; inspect remote object/listing/job status before acting. Append a reconciliation record without rewriting the original attempt | Found object: record its ID and verify it without repeating the write. Confirmed absent: human may authorize retry. Still uncertain: hold |
| Duplicate creation | Retain both IDs/receipts, stop further attempts and reconcile. Human chooses canonical object and separately approves any unpublish/delete action | Two successful writes for one target/version are rejected, even if one record is later hidden |
| Partial success across channels | Preserve successful target receipts; failed/unverified targets retain their own states; do not relaunch successful targets | One target's success does not make the release batch complete |
| Authentication, quota, permission or processing failure | Record redacted error and target state; stop; require operator resolution and confirm that approval still covers the retry | No invented fallback account or silent visibility change |
| Receipt or local audit persistence fails after a remote write | Preserve recoverable request/job identifiers; classify as uncertain; inspect remote state and repair the evidence record before another write | Do not convert a local logging failure into an automatic duplicate upload |
| Publication later becomes unavailable or incorrect | Append observation and correction/retraction decision; preserve original publication and prior evidence; obtain approval for the revised asset/target | No silent overwriting of history and no claim that unpublishing erases prior exposure |
| Missing follow-up evidence | Record the gap and a human review date; keep routing pending or explicitly archive with findings after review | Do not infer sales, downloads, audience benefit or permanent lane status from the source video's engagement |

Retry budgets, credentials, delivery checks, persistent append-only storage, withdrawal execution and operator identity verification remain **human-run requirements** here. The small checker does not implement them. Its automated checks cover stale/missing approvals, provenance fields, preflight flags, record ordering, uncertain outcomes, reconciliation order, duplicate success and routing evidence.

## Run the offline checks

Requirements: Python 3.10 or newer; no packages, secrets or network access. Run from this repository's root. On Windows, use the Python launcher:

```powershell
py -m unittest discover -s examples/awkward_but_anointed -p "test_*.py" -v
```

On Linux/macOS:

```bash
python3 -m unittest discover -s examples/awkward_but_anointed -p 'test_*.py' -v
```

The suite loads three **fully simulated** records and mutates them to test rejection paths. The actor `SIMULATED_OPERATOR`, `fixture:` evidence references and `example.invalid` URLs are never real approvals or receipts. Synthetic asset hashes refer to literal fixture tokens, not actual artwork, PDFs or videos.

Inspect one synthetic record's consistency:

```powershell
py examples/awkward_but_anointed/validate.py examples/awkward_but_anointed/fixtures/synthetic-pdf.json
```

Expected: `consistent`, exit 0. This means only that the assertions fit the reference rules. The checker does not authenticate people, inspect media, dereference evidence, enforce historical immutability, or verify a live publication. A fabricated but internally consistent record can pass; external truth still requires the retained source evidence and human review.

Inspect the historical record:

```powershell
py examples/awkward_but_anointed/validate.py examples/awkward_but_anointed/fixtures/historical-merchandise.json
```

Expected: `hold`, exit 1, with missing hashes, approvals, preflight, receipt and follow-up evidence identified. This is the intended result, not a failed historical release or a reason to invent missing fields.

### Optional pinned-source probe

Use a separate Signal Agent checkout or source slice containing the four files listed in `probe_signal_agent.py`, with the exact LF bytes from commit `fb2918bcf4559bdec37b8367ec458dff2528db11`. The example below assumes that source is in the sibling directory `../signal_agent`; do not reset an active working tree to prepare it. A byte mismatch stops the probe rather than silently testing a different revision.

```powershell
py examples/awkward_but_anointed/probe_signal_agent.py --source ../signal_agent
```

The probe uses only temporary state and an injected fake uploader; it does not invoke the full CLI, read credentials, render actual media, push a site or publish a product/video. Its eight checks characterize the pinned source, including limitations. They are separate from the proposed reference contract's tests.

## Recorded validation result

Run date: **2026-10-27**.

| Check | Result | Claim boundary |
| --- | --- | --- |
| Reference behavior suite | 23 tests passed, including subcases for all three formats | Shared proposed record structure and listed rejection paths work offline |
| Historical fixture | Hold, as expected | Owner-reported completion is preserved without fabricating a complete audit trail |
| Pinned Signal Agent probes | 8 passed | Exact source behavior with temporary state and fake media/uploader; limitations reproduced |
| Live merchandise/PDF/video publication | Not run | No integration or new release is claimed |
| Permanent lane promotion | Pending for historical case | No lane was created or assigned |

## Manual acceptance exercise for a later authorized release

1. Select one bounded campaign and one target. Preserve the signal and G1 decision.
2. Prepare a real merchandise, PDF or video asset. Capture source lineage, output bytes/hash, version and complete packet. Record G2 after review.
3. Stage it through an already verified mechanism or a human-operated tool. Complete the format-specific checks; record G3 for the exact account, channel, content and visibility.
4. Only when publication itself is separately authorized, perform one write and preserve the attempt/response. If uncertain, reconcile before any retry.
5. Inspect the delivered result. Retain receipt, public URL, provider ID, approved-version mapping and human verification. Record partial failures individually.
6. Observe at the declared review window. Separate original-signal performance from derivative outcomes; decide G4, including retirement or archive when appropriate.

Completing this GitHub reference case authorizes none of those later external writes. A successful rehearsal supports the evidence model; a live claim requires an actual approved release and its records.
