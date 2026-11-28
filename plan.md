# Plan — Ovenbrook demo page

Line 1 — kind: **place** (a sourdough bakery in Leith, Edinburgh). Sold: bread and cakes to order.
Main action: **Order a cake** (mailto stand-in `hello@ovenbrook.example`). Material: three library
photographs (stand-ins for the client's own), hours and prices assumed and marked `data-assumed`.

Line 2 — deal:
- palette **mint-pink-accounts** — an off-white flour ground with the deep green of a bakery's tiled wall; made for bakery
- pairing **lora** (Lora / Nunito Sans, serif display 400)
- hero **place** (printed, never dealt): the client's photograph full-bleed, h1 "Sourdough bakery in Leith", one button
- nav **nav-split** · footer **footer-visit** · rhythm **colour-band** (the close on `.ground-brand`, no name across the footer) · buttons **solid** · mark **stack**
- offer composition tall-small → **not used as dealt**: the short page builds the dealt groups and the photograph in one row (two groups on span-3, `pl-photo` span-6 at 3:2)
- place composition **pair** — not used (short page drops the place section)
- type moment **name** — not used (short page drops the type moment)
- rooms layout **side** — not used (no rooms)
- close **close-photo**: the head row (h2 and one line left, main button right) and the third library frame (m37164269, proving baskets — never used above) filling the `.wrap` down to the links, on `.ground-brand`; under 640 the close takes its own screen (`--hm: 2` via `:has(.close__media)`) and the links the next
- moment **picture-develops** (re-dealt with `--exclude photo-chapters`), on the section photograph

Screens:
1. hero `--h: 1` — oven photograph, what/where, hours fact, Order a cake
2. `#shop` `--h: 1` (`--hm: 2` under 640) — h2, group "Today's bake" (4 rows), group "Cakes to order" (4 rows) + the oven photograph (picture-develops), then the visit block: three span-4 columns (address, hours, orders)
3. footer.closing on `.ground-brand` — close head row (Order a cake), links-visit (address 32/40, See the area, hours with today marked), legal row with the credits line

3 screens at 1440 (2,700 px max). Phone bar: one button, Order a cake. Name coined and searched: see `names.json`.
