# Test plan: <project name>

- source: remake/recon.md flows, remake/features.csv
- date:
- tool: <Playwright / the project's runner>

## Flows under test

| flow | happy path | edge cases covered |
| --- | --- | --- |
| F01 | | |

## Matrix

| id | flow | step | kind (happy / edge / state) | automated? | result |
| --- | --- | --- | --- | --- | --- |
| T01 | F01 | | happy | yes | pass |

## State coverage

Every screen from the recon map appears here with the states actually
exercised: empty, loading, filled, error, permission denied, mobile.

## Sign-off

- [ ] all F-priority flows automated
- [ ] no S1 or S2 bugs open
- [ ] states visited for every must-have screen
