# Verification workflow

1. **Build** with the project's own cheap path (demo/fixture mode, no network, no paid calls). Read AGENTS.md/README for rules like "never run the real pipeline for UI work".
2. **Serve over HTTP** (file:// is often blocked in browser tools): `python3 -m http.server <unique-port> --bind 127.0.0.1` from the output folder. Use a new port per build and kill old ones; a shared port can serve another agent's page. Add `?v=N` to dodge caches.
3. **Drive a browser** (Playwright): resize to the app's target width (e.g. 1440x900, also 1280 and 1920), navigate to each view/hash, scroll, screenshot with `scale:"css"`. Screenshots may only be writable inside a specific folder (e.g. the repo's `.playwright-mcp/`, gitignored).
4. **Check persistence by scrolling**, not by full-page screenshots. Full-page capture draws `position:fixed` layers only at the top, which falsely looks like "scenery ends after one screen".
5. **Bare-scene check**: hide the content (`document.querySelector('main').style.visibility='hidden'`, re-show any dock) to judge placement, crop edges and layering.
6. **Motion**: Playwright may report `prefers-reduced-motion: reduce`, which silently disables animation. Emulate `reducedMotion:"no-preference"`, reload, confirm with `matchMedia`. For stable stills: `document.getAnimations().forEach(a=>{a.pause();a.currentTime=ms})`. Count running animations at several scroll depths (should not drop to zero). Then test reduced-motion shows rest poses and 0 running.
7. **Checklist**: every view at top/middle/bottom; no halos or straight crop edges; subjects face the right way; scenery visible not hidden by masks; text legible over bright areas; contrast/forced-colors fallback; no console errors; hover/click on buttons, tabs, tooltips still work.
8. `browser_take_screenshot` may ignore `clip`: crop with `magick shot.png -crop WxH+X+Y +repage out.png` (add `-resize 200%`).
9. Run the project's tests and linter.

## Auditing against the style
Use the critique checklist in `design-language.md`. When using subagents to audit, run one per source (reference images, an article, a spec), merge into a deduplicated action table with a source column; items found by 2+ agents are reliable, single-source items are low confidence. Cross-check each agent's per-image claims against the actual files. Ask "could not reproduce" bug reporters to say so; a fix from code reading stays unverified until the owner checks.
