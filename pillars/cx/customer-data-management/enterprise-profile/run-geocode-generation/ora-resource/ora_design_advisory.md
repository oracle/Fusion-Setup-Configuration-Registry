# Design Advisory

## Guidance Sources

| Source Mode | Allowed Sources | When Used |
|---|---|---|
| Current Oracle behavior | https://docs.oracle.com/en/cloud/saas/sales/fauss/populate-location-latitude-and-longitude-information.html | Explain process purpose, prerequisites, parameters, compatibility, and result boundaries |
| Current setup guidance | https://docs.oracle.com/en/cloud/saas/applications-common/26b/facia/set-up-geocoding.html | Explain how geocoding is enabled for a country |
| Current country-code reference | https://docs.oracle.com/en/cloud/saas/customer-data-management/faicd/list-of-available-countries-with-loqate-geography-reference-data.html | Resolve documented country names and two-letter codes |
| SME decisions | Slack group DM C0BMJ2SPTQE on 2026-08-03 | Apply optional-parameter behavior, Batch Size default 50, maximum 100, and Regenerate Geocode default N |
| Core runtime contract | core.fusion-api.ess-job-submitter | Explain submission, requestId capture, polling, timeout, and resume behavior |

## Guidance Topics

| Topic | Advisory Level | What To Explain | Do Not Include |
|---|---|---|---|
| Process purpose | Strong | The process populates latitude and longitude for eligible active verified addresses | Do not claim it creates geography structures or hierarchy data |
| Parameterless mode | Strong | The process considers eligible addresses for countries where geocoding is enabled | Do not imply every address will receive a match |
| Country-scoped mode | Strong | Resolve a country name, alias, common misspelling, or code and use the documented two-letter code to limit the intended address population | Do not invent a code or silently choose an ambiguous country |
| Date range | Strong | Start Date and End Date filter by location last update date; accept the Fusion UI's M/D/YY style but send YYYY-MM-DD to ESS | Do not pass slash-formatted dates to ESS, silently reverse, or partially apply a range |
| Regeneration | Strong | Y includes records whose coordinates are already populated; N skips them | Do not default to Y |
| Batch sizing | Strong | Default and recommended value is 50; SME-confirmed maximum is 100 | Do not recommend values above 100 |
| Completion | Strong | A successful parent request proves process completion, not universal address match success | Do not claim all selected addresses were geocoded |

## Output Rules

| Situation | What Happens |
|---|---|
| User asks what the skill does | Explain parameterless and parameterized submission plus status monitoring |
| User requests Regenerate Geocode Y | Include a clear reprocessing warning in preview |
| The ESS request succeeds | Report requestId and terminal status; recommend checking process output for selected and unmatched counts when needed |
| The ESS request remains running | Report pending status and retain the requestId |
| The job produces no child requests | Explain that no eligible address may have been selected; do not report an API failure solely for that reason |

## User-Friendly Parameter Prompt

| Situation | Guidance |
|---|---|
| Direct run with unstated scope | Ask whether to run for all eligible addresses in geocoding-enabled countries or narrow it to a specific country or other filters |
| User chooses all eligible addresses | Run without ESS business parameters after resolving monitoring behavior |
| User wants to narrow the run | Ask once for any desired Country Name or Code, Start Date, End Date, Regenerate Geocode, or Batch Size values |
| User supplies a country name or obvious misspelling | Resolve and disclose the canonical country name and code; ask only when the match is ambiguous |
| Parameter help is useful | Link to https://docs.oracle.com/en/cloud/saas/sales/fauss/populate-location-latitude-and-longitude-information.html#Parameters |
| Batch-size guidance | State that current public documentation lists maximum 50, while the task SME confirmed runtime normalization up to 100; recommend 50 |
