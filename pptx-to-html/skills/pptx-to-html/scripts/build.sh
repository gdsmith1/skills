#!/usr/bin/env bash
# Convert a .pptx to ONE self-contained .html presentation, then verify it.
# Deterministic. Run scripts/setup.sh once first.
#
#   scripts/build.sh <deck.pptx> [out_dir]
#
#   out_dir   render workspace (default: site). Holds the rendered slide PNGs
#             (slides/), notes, and GIF overlays. The shareable deliverable is
#             written next to it as <out_dir>.html. Eyeball out_dir/slides/ to
#             confirm fonts/visuals, then you can delete out_dir/ — keep the .html.
#
# Exit codes: 0 ok · 2 bad args · 3 missing render deps · 4 missing verify venv
# · non-zero from verify.py if the built .html fails checks.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # scripts/
VENV="${PPTX2HTML_VENV:-$HOME/.cache/pptx2html/venv}"

PPTX="${1:-}"
OUT="${2:-site}"
[ -n "$PPTX" ] || { echo "usage: build.sh <deck.pptx> [out_dir]"; exit 2; }
[ -f "$PPTX" ] || { echo "ERROR: file not found: $PPTX"; exit 2; }

have() { command -v "$1" >/dev/null 2>&1; }
soffice_ok() { have soffice || have libreoffice || [ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]; }

soffice_ok    || { echo "ERROR: LibreOffice missing. Run scripts/setup.sh"; exit 3; }
have pdftoppm || { echo "ERROR: pdftoppm missing. Run scripts/setup.sh"; exit 3; }
have python3  || { echo "ERROR: python3 missing.";                        exit 3; }
have magick   || { echo "ERROR: ImageMagick missing (needed for WebP embedding). Run scripts/setup.sh"; exit 3; }
[ -x "$VENV/bin/python" ] || { echo "ERROR: Playwright venv missing. Run scripts/setup.sh"; exit 4; }

SINGLE_HTML="${OUT%/}.html"
echo ">> rendering: $PPTX -> $OUT/"
python3 "$DIR/pptx2html.py" "$PPTX" "$OUT"
echo ">> packing single file: $SINGLE_HTML"
python3 "$DIR/singlefile.py" "$OUT" "$SINGLE_HTML"
echo ">> verifying: $SINGLE_HTML"
"$VENV/bin/python" "$DIR/verify.py" "$SINGLE_HTML"

echo ">> done. Shareable file: \"$SINGLE_HTML\"   Render workspace: $OUT/ (eyeball $OUT/slides/, then delete if you like)"
echo ">> preview:  $DIR/preview.sh \"$SINGLE_HTML\"   (or open the .html by double-click)"
