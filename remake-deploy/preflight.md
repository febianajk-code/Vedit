# Preflight: <project name>

- date:
- host:
- domain:

## Secrets

- [ ] all keys from `.env.example` present in the host's store
- [ ] no secret appears in the repo, the build log, or this file
- [ ] integration providers documented (which are live, which test)

## Data

- [ ] migrations apply clean on a fresh database copy
- [ ] backup taken and restore rehearsed
- [ ] seed / test data identifiable at a glance

## Build

- [ ] clean checkout builds without warnings that matter
- [ ] the exact commit deployed is tagged

## Runtime

- [ ] error tracking wired and receiving a test event
- [ ] health endpoint answers 200
- [ ] TLS on, http redirects, www/ apex decided

## Smoke test

- [ ] core loop happy path passes on the live URL
- [ ] payment tested with a real small charge (user approved)

## Rollback

- previous known-good deploy:
- database restore command / runbook:
- who flips the switch:
