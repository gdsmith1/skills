#!/usr/bin/env bash
# One-time setup for the pptx-to-html skill (macOS). Idempotent: skips present.
# Installs the renderers via Homebrew and a Python Playwright venv for the
# verifier (a venv avoids macOS's "externally-managed-environment" pip block).
set -euo pipefail
VENV="${PPTX2HTML_VENV:-$HOME/.cache/pptx2html/venv}"
have() { command -v "$1" >/dev/null 2>&1; }
brew_or_die() { have brew || { echo "   ERROR: Homebrew not found. Install from https://brew.sh"; exit 1; }; }

echo ">> LibreOffice (renders slides with full fidelity)"
if have soffice || have libreoffice || [ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]; then
  echo "   present"
else brew_or_die; brew install --cask libreoffice; fi

echo ">> poppler (pdftoppm)"
if have pdftoppm; then echo "   present"; else brew_or_die; brew install poppler; fi

echo ">> ImageMagick (magick, for single-file WebP embedding)"
if have magick; then echo "   present"; else brew_or_die; brew install imagemagick; fi

echo ">> Python Playwright venv ($VENV)"
have python3 || { echo "   ERROR: python3 not found."; exit 1; }
[ -x "$VENV/bin/python" ] || { mkdir -p "$(dirname "$VENV")"; python3 -m venv "$VENV"; }
"$VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
"$VENV/bin/pip" install -q playwright
"$VENV/bin/python" -m playwright install chromium chromium-headless-shell

echo ">> setup complete. Build a deck:  scripts/build.sh \"YourDeck.pptx\" out [--single]"
