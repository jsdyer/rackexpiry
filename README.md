# Rack Expiry

Private software inventory and support-window planner. Live: https://coolcode.ca/rackexpiry/

<!-- coolcode:guide -->
Add an asset label, software product and installed version. Rack Expiry matches the longest numeric release cycle from a saved endoflife.date catalogue, then sorts support-ended and upcoming deadlines first. Choose an assessment date, inspect the release reference, and export results as CSV. Imports accept simple three-column CSV (asset,product,version) or a JSON array; exported CSV files include evidence columns and can be imported again using their named inventory fields. CSV prefixes formula-leading cells for spreadsheet safety, which can alter labels on reimport; choose **Save inventory JSON** for a lossless backup and exact roundtrip.

Inventory stays in memory until **Save on this device**; only that explicit action writes namespaced local storage. No inventory fields are uploaded. The example stack is illustrative. Standard upstream support, active support and extended support differ: purchased entitlements and distribution backports must be checked separately. Unknown versions stay unknown. Numeric prefix matching requires an entirely numeric installed version; nonnumeric release-cycle names match exactly, ignoring case. Prerelease or malformed suffixes are not treated as stable releases. A support deadline is not proof of an exploitable vulnerability. Upstream deadline dates are the last supported day (the status changes the following day). Boolean-only statuses with no known end date are used only on the catalogue check date, so historical or future assessments remain unknown instead of inventing coverage. The API’s `isMaintained` flag can include extended support and is not used to infer standard support.

The selected product catalogue refreshes Mondays at 10:43 UTC. Changed catalogues are retained as immutable compressed JSON archives with hashes, dates and a change feed; a first capture is a baseline, not retroactive history. The public app works from the last validated saved snapshot. No API key is needed.
<!-- /coolcode:guide -->

## Source and licence

[endoflife.date API v1](https://endoflife.date/docs/api/v1/) is community-maintained. Each product links back to upstream vendor policy. [Source data licence](https://github.com/endoflife-date/endoflife.date/blob/master/LICENSE): MIT (Copyright 2020 endoflife.date contributors). The upstream notice is included in `web/endoflife-data-LICENSE.txt` and published with the catalogue. Derived catalogue retains attribution and source links. Software code follows LICENSE in this repository.

## Development

`python3 scripts/collect.py` explicitly retrieves the catalogue. `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/build.py` validate and build offline. CI runs the browser smoke tests, retains full-page desktop/mobile screenshots for seven days, and publishes Pages only after checks succeed. Failed collections cannot replace the previous deployment. Set optional `HEALTHCHECKS_PING_URL` for collector start/success/failure monitoring; no ping value is included in public files.

## Verified API semantics

API v1 distinguishes `eolFrom` (standard end of life), `eoasFrom` (end of active support), and `eoesFrom` (end of extended support). `isMaintained` can include extended coverage. Definitions: https://github.com/endoflife-date/endoflife.date/blob/master/api_v1/openapi.yml. The date boundary follows the upstream generator’s strict `Date.today > value` comparison: https://github.com/endoflife-date/endoflife.date/blob/master/_plugins/product-data-enricher.rb. Verified 2026-11-22. An unknown extended-support date does not imply ineligibility or entitlement.
