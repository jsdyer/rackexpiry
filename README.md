# Rack Expiry

Private software inventory and support-window planner. Live: https://coolcode.ca/rackexpiry/

<!-- coolcode:guide -->
Add an asset label, software product and installed version. Rack Expiry matches the longest numeric release cycle from a saved endoflife.date catalogue, then sorts support-ended and upcoming deadlines first. Choose an assessment date, inspect the release reference, and export results as CSV. Imports accept simple three-column CSV (asset,product,version) or a JSON array; exported CSV files include evidence columns and can be imported again using their named inventory fields.

Inventory stays in memory until **Save on this device**; only that explicit action writes namespaced local storage. No inventory fields are uploaded. The example stack is illustrative. Standard upstream support, active support and extended support differ: purchased entitlements and distribution backports must be checked separately. Unknown versions stay unknown. A support deadline is not proof of an exploitable vulnerability.

The selected product catalogue refreshes Mondays at 10:43 UTC. Changed catalogues are retained as immutable compressed JSON archives with hashes, dates and a change feed; a first capture is a baseline, not retroactive history. The public app works from the last validated saved snapshot. No API key is needed.
<!-- /coolcode:guide -->

## Source and licence

[endoflife.date API v1](https://endoflife.date/docs/api/v1/) is community-maintained. Each product links back to upstream vendor policy. [Source data licence](https://github.com/endoflife-date/endoflife.date/blob/master/LICENSE.txt): CC BY-SA. Derived catalogue retains attribution and source links. Software code follows LICENSE in this repository.

## Development

`python3 scripts/collect.py` explicitly retrieves the catalogue. `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/build.py` validate and build offline. CI runs the browser smoke tests, retains full-page desktop/mobile screenshots for seven days, and publishes Pages only after checks succeed. Failed collections cannot replace the previous deployment. Set optional `HEALTHCHECKS_PING_URL` for collector start/success/failure monitoring; no ping value is included in public files.
