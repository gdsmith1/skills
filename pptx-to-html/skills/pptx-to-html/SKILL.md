---
name: pptx-to-html
description: >-
  Convert a PowerPoint (.pptx) deck into a single self-contained HTML file that
  preserves every visual exactly — slides are rendered by LibreOffice, so fonts,
  colors, code syntax highlighting, and layout are faithful — along with the
  speaker notes. The one file has no dependencies (opens by double-click), works
  offline, and ships a built-in viewer with a speaker-view pop-up (current + next
  slide, notes, timer). Use this whenever someone wants to turn a PowerPoint /
  .pptx into HTML or a web page, put a slide deck online, present a deck from a
  browser, make a deck viewable or shareable without PowerPoint, export/convert
  PowerPoint to HTML, or get a single-file HTML version of slides — even if they
  don't say "HTML" by name (e.g. "put these slides on the web", "send the deck as
  a link", "make my pptx viewable without PowerPoint", "turn this deck into a
  webpage"). macOS only.
---

# Convert PowerPoint (.pptx) to a self-contained HTML presentation

This skill renders a `.pptx` into ONE self-contained `.html` file with full
visual fidelity and carries the speaker notes across. The hard parts (slide
ordering, notes extraction, high-fidelity rendering, verification) are done by
bundled scripts — your job is to run them and confirm the result looks right.

## What you get

- **`out.html`** — ONE self-contained file: every slide embedded as WebP, a tiny
  built-in vanilla-JS viewer, no dependencies, no network. ~3 MB for ~40 slides.
  Opens by double-click. This is what you **share and present from**. Controls:
  `←`/`→`/`Space`/click navigate, **`S`** opens a speaker-view pop-up (current +
  next slide, notes, timer/clock — drive the deck from either window), **`N`**
  toggles an inline notes panel, `F` fullscreen, `#5` in the URL jumps to slide 5.
- **`out/`** — the render workspace (slide PNGs, notes, GIF overlays). Not the
  deliverable; it's where you eyeball fidelity (step 3). Safe to delete after.

## 1. Setup (first run only)

The pipeline needs LibreOffice + poppler + ImageMagick and a Python Playwright
venv (used by the verifier). Install them once:

```bash
scripts/setup.sh
```

It's idempotent and macOS/Homebrew-based. **First run downloads LibreOffice and a
browser — hundreds of MB, a few minutes** — so tell the user that's expected. If
`build.sh` later exits with code **3** (render deps) or **4** (verify venv),
run `setup.sh` and retry.

## 2. Convert + verify

```bash
scripts/build.sh "path/to/Deck.pptx" out
```

This renders the deck, packs `out.html` (the shareable file), and writes the
`out/` render workspace, then runs `verify.py`, which prints per-check `ok` lines
and a final `PASS`/`FAIL`. A non-zero exit means something is genuinely wrong —
read the failed checks; don't paper over them. Quote paths that contain spaces.

## 3. Confirm fidelity yourself (don't skip this)

The verifier proves the file is *structurally* sound — right number of slides,
every embedded image/GIF decodes, notes present, navigation works, the inline
notes panel and the speaker-view pop-up open. But code can't judge whether the
slides *look* right. The real risk is **font substitution**: if the deck uses a
font LibreOffice lacks, it silently swaps another in and text reflows — still a
valid PASS, but visibly off.

You can see images, so use that. After a PASS, **Read a couple of the rendered
slides** — `out/slides/slide-01.png` plus one content-heavy slide (something with
code or dense text) — and sanity-check them against what the deck should look
like. If a font looks wrong, install it and re-run; otherwise you're done.

## 4. Share / view

Send `out.html` — the recipient double-clicks it; no server or network needed.
Locally, `scripts/preview.sh out.html` opens it in the browser. Controls are
listed under **What you get** above.

## How it works (for trust / debugging)

1. Unzips the pptx (it's a zip of XML); reads `presentation.xml` for the true
   slide **order** (`sldIdLst`) and size, and each slide's notes from its linked
   `notesSlide` (body text only — slide-number/footer placeholders skipped).
2. LibreOffice renders `pptx → pdf`; `pdftoppm` renders each page to a ~2000px
   PNG. PDF page order == presentation order == notes order, so notes align.
   (`pptx2html.py` writes the PNGs, `notes.json`, `overlays.json`, `title.txt`.)
3. `singlefile.py` re-encodes the slides to WebP, base64-embeds them along with
   the notes and GIF overlays into one HTML with a small vanilla-JS viewer that
   includes the speaker-view pop-up.

**Animated GIFs:** LibreOffice flattens slides to static PNGs, freezing a GIF on
frame 1. `pptx2html.py` records each GIF's on-slide rectangle (% of the slide) to
`overlays.json` and copies the GIF; the viewer overlays the live GIF at that exact
spot so it plays.

## Files

- `scripts/build.sh` — run this (render + pack + verify)
- `scripts/setup.sh` — one-time dependency install
- `scripts/pptx2html.py` — renders the pptx to slide PNGs + notes + overlays (stdlib only)
- `scripts/singlefile.py` — packs the render workspace into one self-contained `.html`
- `scripts/verify.py` — deterministic checks (runs under the Playwright venv)
- `scripts/preview.sh` — open the built `.html` in the browser

## Notes

- **macOS only** (Homebrew). Don't try to pre-validate the pptx by other means —
  just run `build.sh`; its verifier is the source of truth.
