---
name: frutiger-aero
description: Restyle a web app, dashboard, or HTML report in the Frutiger Aero aesthetic (2004-2013 Windows Vista/7 Aero Glass, glossy gel buttons, frosted glass cards, cyan-to-cobalt skies, lime hills, water, bubbles, wildlife, photographic scenery). Use whenever the user mentions Frutiger Aero, Aero Glass, Vista/Windows 7 look, "Y2K-successor", glossy skeuomorphic nostalgia, aqua/bubbles/dolphins/sky-and-grass themes, or asks to make an existing UI "retro 2000s glossy", "Wii menu / Vista style", or to convert/reskin/theme a page into that style. Also use when adding photographic scenery layers, gel buttons or glass panels to an existing UI, even if they don't say "Frutiger Aero".
---

# Frutiger Aero restyle

Convert an existing web UI into Frutiger Aero without breaking what it does. The style is optimistic tech-meets-nature: glass, gloss, sky, water, light. It is built from **layers**: scenery behind, translucent glass panels over it, glossy controls on the panels.

**This skill composes a scene, it does not copy one.** Frutiger Aero is a large vocabulary of motifs (city skylines, birds, fish, monitors, globes, bubbles, balloons, dew leaves...). Each run must draw a *different random subset* from the catalogue so results vary, and the user can then swap items. No questions needed to get started.

Read the references as needed:
- `references/motifs.json` + `scripts/pick_motifs.py`: the motif catalogue (90+ items) and the random picker. **Required every run.**
- `references/design-language.md`: what the style is, palette, how it differs from neighbours (read first).
- `references/css-recipes.md`: tokens, glass, gel buttons, title strips, dock, scrollbars, animation, performance (read when writing CSS).
- `references/scenery-assets.md`: photographic cutouts, licensing, inlining, layer/z-index plan (read for Tier 3 or any image).
- `references/verification.md`: how to build, screenshot and audit (read before declaring done).

## Workflow

1. **Inspect the app first.** Find where CSS lives, how the page is built (static HTML, templates, React, a generator that emits one HTML file), and layout constraints (desktop only? single self-contained file? offline?). Do not change behaviour or data; this is a skin. Note the DOM classes for cards, buttons, headings, tables, inputs, tabs, nav, and what the app is *about* (its domain).
2. **Pick a fidelity tier** (default Tier 2 without asking; ask only if the user hinted otherwise):
   - **Tier 1, UI-only:** CSS-only motifs (glass, gel, gradients, bubbles, sparkles). No image files.
   - **Tier 2, layered scene:** Tier 1 plus procedural SVG/CSS scenery.
   - **Tier 3, photographic:** Tier 2 plus real public-domain photo cutouts. Needs the asset pipeline.
3. **Roll the motifs.** Run `python3 <skill>/scripts/pick_motifs.py --tier <N> --theme "<domain words>"` (add `--json` if handy). It returns a random pick per category (sky, ground, water, city, wildlife, objects, particles, UI chrome, people, type). The theme words only nudge the odds. **You must use the roll**: do not swap in your favourites, do not re-roll to get something safer or more familiar, and do not fall back to the same sky + hills + dolphin + monitor set every time. If a pick truly cannot work (needs an asset you cannot legally source, or clashes with the app's function), replace it with another motif from the same category via a second pick, and say so.
   - The **baseline always applies** regardless of the roll: cobalt-to-cyan sky gradient, glass panels, gel buttons, glass nav, legible navy text, and a few bubbles. The roll decides the *distinctive* scenery, props and chrome on top.
   - Write the picks and seed down (in the summary and as a comment at the top of the stylesheet) so the user can reproduce or edit them: "seed 345523: sky-plane, ground-tree, ...".
4. **Tell the user their roll, then proceed** (one short message, no waiting): list the picks with names, and say they can ask to swap, remove, add (any id in `motifs.json`), or re-roll with a new seed.
5. **Add one new stylesheet layer loaded last** (e.g. `aero.css`) rather than rewriting existing CSS. Define colours as custom properties on `:root`. Implement each picked motif following its `how` hint plus the recipes; invent clean procedural versions for Tier 1/2, and source assets per `scenery-assets.md` for Tier 3 picks (reusing vetted assets from another repo is fine when they match a pick; do not import extra scenery that was not rolled).
6. **Build in this order:** sky and scenery, glass panels, controls, typography and chrome, motion. Check after each stage; scenery that fights legibility is the commonest failure.
7. **Protect legibility.** Glass backing with blur + brightness lift, navy text, soft white text-shadow glow; text sitting directly on the scene gets its own small glass backing. Place props in margins and low areas, not behind dense content; put anything that behaves like a character (animals, plane, balloon) behind the glass or in the margins.
8. **Compose, don't pile up.** Rolled items are placed across the viewport (sky items high, ground low, objects in margins) with varied scale and depth. If the roll yields few items for a region, leave it as clean sky/water rather than adding unrolled filler.
9. **Verify visually** (see `references/verification.md`): every view, top/middle/bottom, bare-scene check, animations running, reduced-motion, tests/lint.
10. **Report honestly:** the seed and picks, what was restyled, tier, new files, asset licences, anything unverified, and how to swap motifs.

## What Tier 3 means (hard rule)
Tier 3 is **photographic**. Every picked scenery, wildlife, landscape, city and prop motif (categories sky, ground, water, city, wildlife, objects, people) must be built from a real public-domain / CC0 / US-gov photo cutout (or a photo-derived render, per `scenery-assets.md`), not an SVG/CSS drawing. Procedural is acceptable only for UI chrome, type, particles/light effects, and thin support layers (ridge, water band) where no photo is feasible. Search Wikimedia Commons / NOAA / NASA / USFWS / USDA for each pick, cut it out, grade it to the Aero palette, and record it in CREDITS. If after a real search (several queries, several candidates) a pick has no usable photo, report that, and substitute another pick of the same category via a second roll instead of silently drawing a cartoon. Tier 3 output that is mostly SVG illustrations is a failed Tier 3. Expect 8-15 photo assets plus the UI layer.

## Principles that matter (and why)

- **Layers, not decoration.** Scenery is `position:fixed; inset:0; pointer-events:none` so it never blocks clicks and never scrolls away (a scene that ends after one screen looks broken). Content floats on glass above it.
- **Glass is translucent, not white.** About 30% fill with `backdrop-filter` blur + saturate + brightness, a bright 1px edge, a darker bottom edge, a top-left sheen. Opaque white cards read as flat and lose the style.
- **Gel gloss comes from a hard colour split at 50%** plus a top inset highlight and a coloured glow shadow. A smooth gradient alone reads as modern flat-gradient, not Aero.
- **Saturated, optimistic colour.** Cobalt to cyan sky, lime grass, aqua water, white light. Avoid greys, muddy darks and neon purples.
- **Nature is the point.** Sky, grass, water, bubbles, a few animals. Tech chrome alone is just glassmorphism.
- **Restraint with motion.** Animate only `translate/rotate/scale/opacity`; respect `prefers-reduced-motion`. Do not tie scenery to scroll position, mouse position, or write document-wide custom properties on pointermove (caused flicker and full style recalcs in past work). Do not pause animations based on scroll depth.
- **Fall back gracefully.** Provide `@media (prefers-contrast: more)` and `forced-colors: active` rules that hide scenery and use solid panels; keep `backdrop-filter` optional with `@supports`.
- **Prefer procedural over weak assets.** If a photo cutout looks wrong (splash, cirrus, hills), replace it with SVG `feTurbulence`, CSS, or a generated layer rather than fighting the source.
- **Subagent hygiene when parallelising:** give each agent exclusive files, require targeted Edits on shared files, use a unique port per build, and keep a preview on a saturated blue (`#0aa0e0`) for cutouts.

## Things to avoid

- Rewriting the app's structure or markup beyond hooks for the skin (extra `div`s for scenery layers are fine).
- Licences other than CC0 / public domain / US-government works for any bundled photo (no CC-BY, NC, ND). Record every asset in a credits file.
- Fake non-functional UI (decorative min/max/close buttons, inert media-player pills). The owner of the reference project removed these; decorative chrome should not look clickable.
- Mobile layouts unless the app already supports mobile; check the repo's AGENTS.md or README for constraints.
- Heavy files: keep a single-file report near a few MB; tighten widths or quality before adding assets.

## Output expectations

Deliver the working restyle in the repo (new stylesheet + minimal hooks + optional assets), with a short summary: tier chosen, files added/changed, how to rebuild, screenshots viewed, known weak spots.

## Host-app pitfalls (learned from a Bootstrap/Spring Boot test)
- **Host CSS fights your overrides.** Before styling, dump `getComputedStyle` for `table, tr, td, .card, .btn, h1-h3, p, a` and look for dark-theme rules and Bootstrap striping (which paints `tr`, `td` and box-shadow insets). Expect doubled-class selectors or `!important` in the skin layer, and reset text colours that assumed a dark or hero background (white-on-glass).
- **Bootstrap selector map:** `.card`/`.list-group-item`/`.modal-content` -> glass; `.table` -> glass + glossy `thead`; `.btn-primary` -> gel blue/green, `.btn-warning` -> gel sun; `.navbar` -> glass bar with gel pill active link; `.form-control`/`.form-select` -> inset input + cyan focus ring; `.pagination` -> glass capsule.
- **Button shine clips focus rings and tooltips** (`overflow:hidden`). Put the shine on a `::before` with `clip-path: inherit`/inset, or skip it on buttons that host tooltips.
- **Title strips and the dock are optional.** Keep a top navbar as a glass bar if the app has one.
- **Gitignored CSS:** run `git check-ignore -v <new css>`; look for an SCSS/build pipeline as the source of truth before adding raw CSS. Same for image folders.
- **Server-rendered apps (Spring, Rails, Django):** resources are copied to a build dir at startup, so edit-then-reload may serve stale files; copy or rebuild, and bust the cache on the linked CSS too (`fetch(url,{cache:'reload'})` then reload).
- **Repo rules vs a skin:** if AGENTS.md demands TDD for features, treat a pure skin as not a feature, say so, and still run the existing tests.
- **Playwright output folder:** if only a specific folder is writable, save there then `cp` out.
- **Tier 3 shortcut:** if a sibling repo already has vetted PD/CC0 aero assets (e.g. `jev-playlist-bucketer` branch `feat/frutiger-aero`, `bucketer/dashboard/static/img` with CREDITS.md and `aero/*.css|html` lane sources), copy and adapt only the assets/lane code for motifs that were *rolled*, carrying CREDITS rows along. Do not import the whole example scene: that defeats the random roll.

## Tier 3 lessons (pet clinic port)
- **Copy the whole lane set**, not just `hero`/`v3`: hill offsets (`translateY(-27/-17/-6vh)`) live in `polish.css`; without them the hills hide behind the water band. Merge sky, hero, water, animals, bubbles, v3 scene rules, then polish offsets.
- **No dock?** The reference dock covers the last 62px of water. Set `--dock:0px`, trim water height (`clamp(190px,26vh,300px)`), expect hills to sit lower.
- **Glass over bright lime hills goes neon/mint.** Add a slightly darker or bluer tint (and lower `saturate`) on panels that sit over the hill band, or keep dense content (tables, forms) above the hill line with a stronger fill. Blurred skyline behind glass reads as blue smears; fade the skyline where panels overlap.
- **White-background photos:** `mix-blend-mode:multiply` plus a radial `mask-image` blends them into glass; fall back to normal blend under `prefers-contrast`.
- **Host fonts:** override with an explicit selector list, not `*`, so icon fonts (FontAwesome) survive.
- **Spring dev servers:** rsync `src/main/resources` into `target/classes` before checking, and confirm the served CSS actually contains the new rules (a stale cached file cost a debug round).
- **Screenshots:** if the screenshot tool is path-restricted, `page.screenshot({path})` inside `browser_run_code_unsafe` can write elsewhere.
- macOS `sed -i` needs `''`.
- Pages that are short never exercise scroll persistence; test a long page too.

## Roll-workflow clarifications (from the first randomized run)
- **Baseline vs roll:** a rolled variant (e.g. `sky-dusk`) may modify the baseline sky, e.g. cobalt at the top easing into a warm horizon. The baseline guarantees quality, not a specific palette.
- **Support layers are allowed:** if a pick needs a surface (windmills need a ridge; splash, dolphin, frog or seahorse need a water band), add a *minimal* ridge or water band and say it was added as support. Do not add other unrolled scenery.
- **Narrow margins:** when the content container leaves under ~60px margins, anchor props to bands that content does not cover (shoreline, horizon, top sky strip, footer water) and let animals pass behind the glass, instead of relying on side margins.
- **Prop vs chrome:** a prop is a floating scene object (tilted, behind or beside glass, not clickable). Chrome must work. A media-player or clock prop is fine as scenery; never as a fake control in the UI.
- **Reused assets:** the jev cutouts are cropped for their old scenes (splash rotated ~22 degrees, dolphin is a mid-arc pose), so expect rotation and keyframe tuning.
- **Gotchas:** `<use>`-cloned SVG animations share phase (offset with separate elements or delays); `clip-path` clips `filter` glows; for the bare-scene shot hide `main`, not `.container-fluid` (navbars use it too); under reduced motion `animation:none` leaves overlays (eyelids, ripples) at their default opacity, so set rest states explicitly; fonts that are not bundled depend on the network.
