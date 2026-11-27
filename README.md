# The Remake skill

Eleven Claude skills that remake any app. Free, MIT, no signup, no API key,
nothing to connect.

One reverse-engineers the app you want to remake. One rebuilds it. One tests
it for bugs. And one is the Entrepreneur: it reads what the app's users hate
and fixes it in yours, so you have an app you can sell.

In between, the others plan the stack and the database, rebuild the design
system, wire up auth and payments, score your remake against the original,
give it a name and a brand of its own, write the landing page and the store
listing, and put it live on your domain.

**It rebuilds what an app does, never what it owns.** Features and flows,
clean-room style. Not its code, its logo, its copy or its content. The fine
print is at the bottom, and the skills enforce it.

Inspired by and modelled on the [Replica skill](https://github.com/Jakeschincariol/replica-skill)
by Jake Schincariol (MIT).

## Install

Paste this into Claude:

```
https://github.com/febianajk-code/Vedit

install skill
```

Or as a plugin, in Claude Code:

```
/plugin marketplace add febianajk-code/Vedit
/plugin install remake-skill@remake-skill
```

Claude Code namespaces plugin skills, so installed as a plugin they show up
as `/remake-skill:remake-recon` and so on. Copy the folders instead if you
want plain `/remake-recon`:

```bash
git clone https://github.com/febianajk-code/Vedit.git
cp -r Vedit/remake-* ~/.claude/skills/
```

Project-local instead of global: copy the same folders into your repo's
`.claude/skills/`. No Claude Code at all? Paste any single `SKILL.md` at the
top of a chat and it runs as a mode. You lose the Python tools, but the
method works.

The tools need Python 3.8 or newer. Nothing to pip install.

## The eleven

| command | what it does |
| --- | --- |
| `/remake-recon` | Reverse-engineers any app: screens, flows, components, data model. From public pages, screenshots, store listings and your own account. |
| `/remake-architect` | Plans the stack, database schema and API for your remake. |
| `/remake-design` | Rebuilds the design system: colours, type, spacing, components. As tokens, with your own assets. |
| `/remake-build` | Rebuilds the app screen by screen from the recon map. |
| `/remake-backend` | Auth, database, payments and integrations. |
| `/remake-test` | Clicks through every flow and tests it for bugs. |
| `/remake-diff` | Compares your remake against the original. A parity score and what is missing. |
| `/remake-entrepreneur` | Reads what the app's users hate in real reviews and turns it into fixes and a positioning angle. |
| `/remake-brand` | Names and rebrands your version so it is yours. |
| `/remake-launch` | Landing page, pricing and store listing. |
| `/remake-deploy` | Ships it live on your own domain. |

## How to use it

Run them in order. Each one reads what the last one wrote, in a `remake/`
folder in your project.

```
recon -> architect -> design -> build -> backend -> test -> diff -> entrepreneur -> brand -> launch -> deploy
```

An example: remaking a scheduling app, the kind where you share a link and
people book a time with you.

1. **`/remake-recon`** with the app's URL. It reads the help center, the
   pricing page, the store listing and public walkthroughs, and you click
   through your own account with it. Out comes `remake/recon.md`: 18
   screens, 7 flows, the components, an inferred data model and
   `features.csv`. The partner marketplace is marked out of scope: that is
   their network, not a feature.
2. **`/remake-architect`** picks Next.js, Postgres, Stripe and Resend, writes
   the schema (with a constraint so two guests can never book the same slot)
   and orders the build: the booking flow end to end first.
3. **`/remake-design`** measures the screenshots into tokens: colour roles,
   type scale, 8px spacing, the date picker and slot button specs. Open
   icons, an open font, your own words. The contrast tool signs off on every
   text/background pair.
4. **`/remake-build`** builds the shell, then the booking flow, then every
   screen with all its states, ticking off `features.csv` as it goes.
5. **`/remake-backend`** adds sign up, calendar sync through the provider's
   own API with your keys, Stripe for paid bookings, reminder emails.
6. **`/remake-test`** writes a test plan from the 7 flows, Playwright specs
   for the happy paths and edge cases (time zones, a slot taken mid-booking,
   double submit), and logs bugs by severity until no S1 or S2 is open.
7. **`/remake-diff`** scores it. Features 86, all must-haves done, the two
   weakest areas named, the build order for the gap.
8. **`/remake-entrepreneur`** reads the store reviews. The loudest complaint
   is reminders that arrive at midnight; that fix becomes a `must` row and
   the headline of the landing page.
9. **`/remake-brand`** names it, shifts the palette, sweeps the codebase
   until no string from the original survives.
10. **`/remake-launch`** writes the landing page, three pricing tiers and a
    store listing that `listing.py` validates before the store does.
11. **`/remake-deploy`** preflight, staging, smoke test, live domain, and
    the rollback written down before anyone needs it.

## The tools

Every tool is standard library only. No pip install, no network calls.

| tool | folder | what it does |
| --- | --- | --- |
| `contrast.py` | remake-design | WCAG contrast for every text/background pair in tokens.json |
| `parity.py` | remake-diff | Feature parity score from features.csv, 80/20 with layout |
| `imgdiff.py` | remake-diff | Screenshot layout comparison, structure not colour |
| `reviews.py` | remake-entrepreneur | Buckets reviews into themes and ranks the complaints |
| `sweep.py` | remake-brand | Finds leftover strings from the original app |
| `listing.py` | remake-launch | Validates the store listing before submission |

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

## Fine print

Read this before you sell anything you build with this pack.

- **You get the features, not the property.** Clean-room, reverse-engineered
  from public behaviour: no decompiling, no copied assets, no lifted copy.
- **Names and marks are checked, not cleared.** The brand skill runs a
  first-pass sanity check and flags collisions; it is not legal advice and
  does not replace a lawyer.
- **Terms still apply to you.** Some products forbid using your account to
  build a competitor. The recon skill asks you to check yours before it
  starts.
- **Regulated data is out of scope.** Banking, health, and anything with a
  licence attached: the skills will refuse and tell you why.
- **You ship it, you own it.** Testing, privacy policy, store review, taxes:
  the skills prepare the ground, the launch is yours.

## License

MIT. See [LICENSE](LICENSE).
