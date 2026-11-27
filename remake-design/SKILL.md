---
name: remake-design
description: >-
  Rebuilds the original app's design system as tokens: colour roles, type
  scale, spacing, radii, shadows and component specs, measured from the
  screenshots in remake/screens/, checked for contrast, and deliberately not
  copying the app's logo, illustrations or copy. Third step of the Remake
  pack. Use when the user says "rebuild the design", "extract the design
  tokens", "make it look like X", or after /remake-architect.
---

# remake-design

Input: `remake/recon.md` (the component list) and the screenshots in
`remake/screens/`. Output: `remake/tokens.json` (template: tokens.json in
this folder) and a component spec section appended to `remake/architecture.md`.

## The rules

- **Measure, do not trace.** Tokens describe sizes, spacing and colour
  roles. The remake draws its own icons, uses an openly licensed typeface,
  and writes its own words.
- **No asset lifting.** Never copy the original's logo, illustrations,
  onboarding copy or marketing images into the remake or into tokens.
- **Roles, not hexes, in the app.** The app consumes `color.surface`,
  `color.text.muted` and `space.md`. Raw hex values live only in tokens.json
  and the theme file that maps them.

## Step 1: harvest from screenshots

Open the clearest screenshot per key screen from `remake/screens/` and
record:

- **Colour roles.** Surface, background, text, text-muted, primary,
  primary-text, danger, success, border, focus. Sample the pixels; name the
  role they play, not where they appeared.
- **Type scale.** Body size and line height first, then headings by ratio.
  Note weights actually used.
- **Spacing.** Find the base unit (usually 4 or 8) and measure the common
  paddings and gaps against it.
- **Radii, borders, shadows.** One small set. Most apps use two radii and
  one shadow.

## Step 2: check contrast

Run the bundled tool on every text/background pair:

```bash
python3 contrast.py tokens.json --min 4.5
```

It reads tokens.json, computes WCAG contrast ratios, and exits non-zero on
failure with the failing pairs listed. Fix the tokens, not the tool. Large
display text may pass at 3.0, but body text may not.

## Step 3: component specs

For each component in the recon map's component list, write the spec the
builder needs: padding, radius, type token, state variants (hover, focus,
active, disabled, loading), and the empty and error states. Two components
with the same spec are one component.

## Step 4: theme file

Emit tokens.json with `roles`, `type`, `space`, `radius`, `shadow` and a
`map` from role to value. The app reads the map, so rebranding later means
editing one file. remake-brand relies on this.

## Output

`remake/tokens.json`, contrast check passing, component specs appended to
`remake/architecture.md`, then a summary: token counts, any contrast
exceptions granted, and the next step: `/remake-build`.
