#!/usr/bin/env python3
"""Render a .pptx into the intermediate assets that singlefile.py packs into one
self-contained .html (full visual fidelity + speaker notes).

Visuals are rendered by LibreOffice (fonts, colors, code highlighting, layout).
Speaker notes are extracted from the pptx XML. Animated-GIF placements are
recorded so they can be overlaid live (LibreOffice flattens GIFs to frame 1).

Usage:
    python3 pptx2html.py "Deck.pptx" [output_dir] [--dpi N]

  output_dir   where to write the render assets (default: ./site)
  --dpi N      render resolution (default 150 -> ~2000px wide for 16:9).

Writes into output_dir: slides/slide-NN.png, media/<gif>, notes.json,
overlays.json, title.txt. Pack these into one shareable .html with singlefile.py
(build.sh runs both for you).

Requires: LibreOffice (soffice), pdftoppm (poppler), python3.
"""
import sys, os, re, json, glob, shutil, subprocess, tempfile, zipfile
import xml.etree.ElementTree as ET

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'a': A, 'p': P}
SKIP_PH = {'sldImg', 'sldNum', 'dt', 'ftr'}          # not speaker-note text


def die(msg):
    sys.exit('ERROR: ' + msg)


def find_soffice():
    for c in ('soffice', 'libreoffice',
              '/Applications/LibreOffice.app/Contents/MacOS/soffice'):
        path = shutil.which(c) if not c.startswith('/') else (c if os.path.exists(c) else None)
        if path:
            return path
    die('LibreOffice not found. Install: brew install --cask libreoffice')


def text_of_paragraphs(txbody):
    out = []
    for para in txbody.findall('a:p', NS):
        out.append(''.join(t.text or '' for t in para.iter('{%s}t' % A)))
    return '\n'.join(out).strip()


def extract_notes(notes_path):
    """Return the speaker-note text from a notesSlideN.xml (body placeholder only)."""
    root = ET.parse(notes_path).getroot()
    chunks = []
    for sp in root.iter('{%s}sp' % P):
        ph = sp.find('.//p:nvSpPr/p:nvPr/p:ph', NS)
        if ph is not None and ph.get('type') in SKIP_PH:
            continue
        tb = sp.find('.//p:txBody', NS)
        if tb is not None:
            chunks.append(text_of_paragraphs(tb))
    return '\n'.join(c for c in chunks if c).strip()


def rels_targets(rels_path):
    """Map Relationship Id -> Target for a .rels file (empty if missing)."""
    if not os.path.exists(rels_path):
        return {}
    root = ET.parse(rels_path).getroot()
    return {rel.get('Id'): rel.get('Target')
            for rel in root.findall('{%s}Relationship' % PKG)}


def ordered_slide_data(unzip_dir, media_out, cx, cy):
    """Per-slide data in true presentation order (sldIdLst): speaker notes plus
    animated-GIF overlays. LibreOffice flattens slides to a static image, so an
    embedded GIF freezes on frame 1; we record each GIF's on-slide rectangle (as
    CSS %) and copy the original file so it can be overlaid live in the HTML.
    Returns a list of {'notes': str, 'gifs': [{file,left,top,w,h}, ...]}."""
    pres = os.path.join(unzip_dir, 'ppt', 'presentation.xml')
    id2target = rels_targets(os.path.join(unzip_dir, 'ppt', '_rels', 'presentation.xml.rels'))
    root = ET.parse(pres).getroot()
    data, copied = [], set()
    for sld in root.iter('{%s}sldId' % P):
        rid = sld.get('{%s}id' % R)
        target = id2target.get(rid, '')                       # e.g. slides/slide3.xml
        slide_name = os.path.basename(os.path.normpath(os.path.join('ppt', target)))
        slide_rels = rels_targets(os.path.join(unzip_dir, 'ppt', 'slides', '_rels', slide_name + '.rels'))

        notes_text = ''
        for tid, tgt in slide_rels.items():
            if 'notesSlide' in (tgt or ''):
                notes_abs = os.path.normpath(os.path.join(unzip_dir, 'ppt', 'slides', tgt))
                if os.path.exists(notes_abs):
                    notes_text = extract_notes(notes_abs)
                break

        gifs = []
        slide_xml = os.path.normpath(os.path.join(unzip_dir, 'ppt', target))
        if os.path.exists(slide_xml):
            for pic in ET.parse(slide_xml).getroot().iter('{%s}pic' % P):
                blip = pic.find('.//a:blip', NS)
                emb = blip.get('{%s}embed' % R) if blip is not None else None
                tgt = slide_rels.get(emb, '') if emb else ''
                if not tgt.lower().endswith('.gif'):
                    continue
                xfrm = pic.find('.//a:xfrm', NS)
                off = xfrm.find('a:off', NS) if xfrm is not None else None
                ext = xfrm.find('a:ext', NS) if xfrm is not None else None
                if off is None or ext is None:
                    continue                                  # inherited geometry — skip
                src_abs = os.path.normpath(os.path.join(unzip_dir, 'ppt', 'slides', tgt))
                base = os.path.basename(src_abs)
                if base not in copied:
                    os.makedirs(media_out, exist_ok=True)
                    shutil.copy(src_abs, os.path.join(media_out, base))
                    copied.add(base)
                x, y, ecx, ecy = (int(off.get('x')), int(off.get('y')),
                                  int(ext.get('cx')), int(ext.get('cy')))
                gifs.append({'file': 'media/' + base,
                             'left': '%.3f%%' % (x / cx * 100), 'top': '%.3f%%' % (y / cy * 100),
                             'w': '%.3f%%' % (ecx / cx * 100), 'h': '%.3f%%' % (ecy / cy * 100)})
        data.append({'notes': notes_text, 'gifs': gifs})
    return data


def slide_dimensions(unzip_dir):
    """Return (cx, cy) EMU from sldSz; default 16:9."""
    root = ET.parse(os.path.join(unzip_dir, 'ppt', 'presentation.xml')).getroot()
    sz = root.find('{%s}sldSz' % P)
    if sz is not None:
        return int(sz.get('cx')), int(sz.get('cy'))
    return 12192000, 6858000


def render_pdf(soffice, pptx, workdir):
    subprocess.run([soffice, '--headless', '--convert-to', 'pdf',
                    '--outdir', workdir, pptx],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdfs = glob.glob(os.path.join(workdir, '*.pdf'))
    if not pdfs:
        die('LibreOffice did not produce a PDF.')
    return pdfs[0]


def render_pngs(pdf, slides_dir, dpi):
    os.makedirs(slides_dir, exist_ok=True)
    subprocess.run(['pdftoppm', '-png', '-r', str(dpi), pdf,
                    os.path.join(slides_dir, 'slide')], check=True)
    imgs = glob.glob(os.path.join(slides_dir, 'slide-*.png'))
    imgs.sort(key=lambda p: int(re.search(r'(\d+)\.png$', p).group(1)))  # page order
    return imgs


def main():
    argv = sys.argv[1:]
    if not argv:
        die('usage: python3 pptx2html.py "Deck.pptx" [out_dir] [--dpi N]')
    dpi, positional = 150, []
    i = 0
    while i < len(argv):
        if argv[i] == '--dpi':
            dpi = int(argv[i + 1]); i += 2
        else:
            positional.append(argv[i]); i += 1
    pptx = positional[0]
    out_dir = positional[1] if len(positional) > 1 else 'site'
    if not os.path.exists(pptx):
        die('file not found: ' + pptx)
    if not shutil.which('pdftoppm'):
        die("'pdftoppm' not found. Install: brew install poppler")
    soffice = find_soffice()

    os.makedirs(out_dir, exist_ok=True)
    workdir = tempfile.mkdtemp()
    with zipfile.ZipFile(pptx) as z:
        z.extractall(workdir)

    cx, cy = slide_dimensions(workdir)
    slidedata = ordered_slide_data(workdir, os.path.join(out_dir, 'media'), cx, cy)
    notes = [d['notes'] for d in slidedata]

    pdf = render_pdf(soffice, pptx, workdir)
    images = render_pngs(pdf, os.path.join(out_dir, 'slides'), dpi)
    if len(images) != len(notes):
        print('WARNING: %d rendered pages but %d slides in pptx order; '
              'notes/overlay alignment may be off.' % (len(images), len(notes)))

    title = os.path.splitext(os.path.basename(pptx))[0]
    with open(os.path.join(out_dir, 'title.txt'), 'w') as f:
        f.write(title)
    json.dump({str(i + 1): n for i, n in enumerate(notes)},
              open(os.path.join(out_dir, 'notes.json'), 'w'),
              indent=2, ensure_ascii=False)
    # overlays.json: GIF placements per slide, consumed by singlefile.py
    overlays = {str(i + 1): d['gifs'] for i, d in enumerate(slidedata) if d['gifs']}
    json.dump(overlays, open(os.path.join(out_dir, 'overlays.json'), 'w'), indent=2)

    with_notes = sum(1 for n in notes if n.strip())
    n_gifs = sum(len(d['gifs']) for d in slidedata)
    print('Rendered: %s/  (%d slides, %d with speaker notes, %d animated GIF overlay(s) on %d slide(s))'
          % (out_dir, len(images), with_notes, n_gifs, len(overlays)))
    print('  Pack into one shareable .html:  python3 singlefile.py %s' % out_dir)


if __name__ == '__main__':
    main()
