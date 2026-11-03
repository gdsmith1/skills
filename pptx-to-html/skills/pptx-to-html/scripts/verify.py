#!/usr/bin/env python3
"""Deterministic verification for the single-file .html build. No human judgment.

    <venv>/bin/python verify.py <build.html>

Run with the Playwright venv python created by setup.sh. Exit 0 = PASS, 1 = FAIL.

Checks (loaded via file://, exactly how a recipient opens it): no external deps,
every embedded image/GIF decodes, notes present, navigation works, the inline
notes panel (N) opens, and the reveal-style speaker-view pop-up (S) opens with a
current + next slide. Code can't judge whether fonts/visuals look right — eyeball
the rendered slides/ PNGs for that.
"""
import sys, os, re, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

fails = []
def check(cond, msg):
    print(("  ok  " if cond else "  XX  ") + msg)
    if not cond:
        fails.append(msg)
def report(summary):
    print()
    if fails:
        print("FAIL (%d):" % len(fails))
        for f in fails:
            print("  - " + f)
        sys.exit(1)
    print("PASS: " + summary)
    sys.exit(0)


def verify_single(file):
    print("STATIC checks:")
    txt = open(file).read()
    check(bool(re.search(r"data:image/(webp|png|jpeg);base64,", txt)), "images are embedded as data URIs")
    check(not re.search(r"<script[^>]+src=", txt) and not re.search(r"<link[^>]+href=", txt),
          "no external script/link dependencies")

    url = Path(os.path.abspath(file)).as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 900})
        page = ctx.new_page()
        print("LIVE checks (file://):")
        page.goto(url, wait_until="load")
        page.wait_for_function("() => window.deck && window.deck.total > 0", timeout=30000)
        total = page.evaluate("() => window.deck.total")
        notes_len = page.evaluate("() => window.deck.notes.length")
        check(total > 0, "viewer reports %d slides" % total)
        check(notes_len == total, "notes array length (%d) matches slide count (%d)" % (notes_len, total))
        bad = page.evaluate("""async () => {
            const out = [];
            for (let k = 0; k < window.deck.images.length; k++) {
                const img = new Image(); img.src = window.deck.images[k];
                try { await img.decode(); } catch { out.push(k + 1); }
            }
            return out;
        }""")
        check(len(bad) == 0, "all %d embedded images decode%s" % (total, "" if not bad else " (bad: %s)" % bad))
        gif_n = page.evaluate("() => (window.deck.gifs || []).length")
        if gif_n:
            badg = page.evaluate("""async () => {
                const out = [];
                for (let k = 0; k < window.deck.gifs.length; k++) {
                    const im = new Image(); im.src = window.deck.gifs[k];
                    try { await im.decode(); } catch { out.push(k + 1); }
                }
                return out;
            }""")
            check(len(badg) == 0, "all %d embedded GIF(s) decode%s" % (gif_n, "" if not badg else " (bad: %s)" % badg))
        page.evaluate("() => window.deck.go(1)")
        check(page.evaluate("() => window.deck.index") == 1, "navigation advances slides")
        page.evaluate("() => window.deck.go(0)")

        # inline notes panel (N)
        page.keyboard.press("n")
        check(page.evaluate("() => window.deck.notesOpen"), "pressing N opens the inline notes panel")

        # speaker-view pop-up (S) — reveal-style: current + next slide, notes, timer
        sp_title, sp_imgs = "", False
        try:
            with ctx.expect_page(timeout=10000) as pinfo:
                page.keyboard.press("s")
            sp = pinfo.value
            sp.wait_for_load_state("domcontentloaded")
            sp.wait_for_function(
                "() => { const c=document.getElementById('curimg'); return c && c.src && c.src.indexOf('data:')===0; }",
                timeout=10000)
            sp_title = sp.title()
            sp_imgs = sp.evaluate("""() => {
                const cur=document.getElementById('curimg'), nx=document.getElementById('nximg');
                const curOk = !!(cur && cur.src.indexOf('data:')===0);
                const nxOk  = !!(nx && (nx.style.display==='none' || nx.src.indexOf('data:')===0));
                return curOk && nxOk;
            }""")
            sp.screenshot(path=os.path.join(tempfile.mkdtemp(prefix="verify-"), "speaker-view.png"))
        except Exception:
            pass
        check(page.evaluate("() => window.deck.speakerOpen"), "pressing S opens the speaker-view pop-up")
        check("speaker view" in sp_title.lower(), 'speaker-view window titled correctly (title: "%s")' % sp_title)
        check(sp_imgs, "speaker view shows the current slide (and next-slide preview)")

        shot = os.path.join(tempfile.mkdtemp(prefix="verify-"), "singlefile-preview.png")
        page.screenshot(path=shot)
        print("  (preview screenshot: %s)" % shot)
        b.close()
    report("standalone file OK — open %s by double-clicking; no server or network needed." % file)


def main():
    target = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "site.html")
    if not os.path.exists(target):
        print("FAIL: target not found: " + target); sys.exit(1)
    if os.path.isfile(target):
        verify_single(target)
    else:
        print("FAIL: %s is a directory. Pass the built .html file (e.g. site.html), "
              "not the render workspace." % target); sys.exit(1)


if __name__ == "__main__":
    main()
