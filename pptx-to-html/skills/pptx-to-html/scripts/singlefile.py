#!/usr/bin/env python3
"""Pack a pptx2html.py build into ONE self-contained .html file.

No reveal.js, no external files: every slide image is re-encoded to WebP and
base64-embedded, with a tiny vanilla-JS viewer (arrows/space/click navigate, S
opens a reveal-style speaker-view pop-up with next-slide preview + notes + timer,
N toggles an inline notes panel, F fullscreen). Animated GIFs (from overlays.json)
are embedded and overlaid at their on-slide rectangle so they play. The result is
a single file you can email/drop anywhere and open by double-clicking.

    python3 singlefile.py <build_dir> [output.html] [--quality N] [--format webp|png]

  build_dir   a folder produced by pptx2html.py (has slides/ and notes.json)
  output.html default: <build_dir basename>.html next to the build dir
  --quality   WebP quality 1-100 (default 82; text stays crisp, small files)
  --format    webp (default, needs ImageMagick `magick`) or png (no re-encode)
"""
import sys, os, re, json, glob, base64, subprocess, html


def die(m): sys.exit('ERROR: ' + m)


def encode_image(png_path, fmt, quality):
    if fmt == 'png':
        data = open(png_path, 'rb').read()
        return 'data:image/png;base64,' + base64.b64encode(data).decode()
    out = subprocess.run(['magick', png_path, '-quality', str(quality), 'webp:-'],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if out.returncode != 0 or not out.stdout:
        die('magick failed on %s: %s' % (png_path, out.stderr.decode()[:200]))
    return 'data:image/webp;base64,' + base64.b64encode(out.stdout).decode()


def encode_gif(path):
    return 'data:image/gif;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def read_title(build_dir):
    tf = os.path.join(build_dir, 'title.txt')
    if os.path.exists(tf):
        t = open(tf).read().strip()
        if t:
            return t
    return os.path.basename(os.path.abspath(build_dir).rstrip('/'))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  html,body{margin:0;height:100%;background:#0a0e1a;overflow:hidden;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
  /* 16:9 frame fit to the viewport (letterboxed); slide + GIF overlays share it
     so overlays line up at any window size. */
  #stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;}
  #frame{position:relative;width:min(100vw,calc(100vh*16/9));height:min(100vh,calc(100vw*9/16));cursor:pointer;}
  #screen{position:absolute;inset:0;width:100%;height:100%;object-fit:fill;display:block;transition:opacity .12s ease;}
  #giflayer{position:absolute;inset:0;}
  #giflayer .gif{position:absolute;object-fit:fill;}
  #bar{position:fixed;top:0;left:0;height:3px;background:#3aa0ff;width:0;transition:width .2s;z-index:5;}
  #counter{position:fixed;bottom:10px;right:14px;color:#8aa3c0;font:13px/1 ui-monospace,monospace;opacity:.7;z-index:5;}
  #hint{position:fixed;bottom:10px;left:14px;color:#8aa3c0;font:13px/1 sans-serif;opacity:.6;z-index:5;transition:opacity .5s;}
  #hint.gone{opacity:0;}
  #notes{position:fixed;left:0;right:0;bottom:0;max-height:42%;overflow:auto;
    background:rgba(10,14,26,.97);border-top:1px solid #223150;color:#dfe6f2;
    padding:16px 22px 22px;z-index:6;box-shadow:0 -8px 24px rgba(0,0,0,.5);}
  #notes[hidden]{display:none;}
  #notes h3{margin:0 0 8px;font:600 12px/1 sans-serif;letter-spacing:.12em;color:#6cf;text-transform:uppercase;}
  #notesbody{white-space:pre-wrap;font-size:18px;line-height:1.5;max-width:60em;}
</style>
</head>
<body>
  <div id="stage"><div id="frame"><img id="screen" alt=""><div id="giflayer"></div></div></div>
  <div id="bar"></div>
  <div id="counter"></div>
  <div id="hint">← → navigate · S speaker view · N notes · F fullscreen</div>
  <div id="notes" hidden><h3>Speaker notes</h3><div id="notesbody"></div></div>
<script>
const SLIDES = __SLIDES__;
const NOTES  = __NOTES__;
let i = 0;
const screen=document.getElementById('screen'), giflayer=document.getElementById('giflayer'),
      bar=document.getElementById('bar'), counter=document.getElementById('counter'),
      notesEl=document.getElementById('notes'), notesBody=document.getElementById('notesbody'),
      hint=document.getElementById('hint');
function hashIndex(){ const m=location.hash.match(/(\d+)/);
  return m ? Math.min(Math.max(parseInt(m[1],10)-1,0), SLIDES.length-1) : 0; }
function showNotes(){ const t=(NOTES[i]||'').trim();
  notesBody.textContent = t || '(no notes for this slide)'; }
function go(n){
  i=(n+SLIDES.length)%SLIDES.length;
  const s=SLIDES[i];
  screen.style.opacity=0;
  requestAnimationFrame(()=>{ screen.src=s.img; screen.alt='Slide '+(i+1); screen.style.opacity=1; });
  giflayer.innerHTML='';   // rebuild overlays -> GIF replays from frame 1 on each visit
  (s.gifs||[]).forEach(g=>{ const im=document.createElement('img'); im.className='gif';
    im.src=g.src; im.style.left=g.left; im.style.top=g.top; im.style.width=g.w; im.style.height=g.h;
    giflayer.appendChild(im); });
  counter.textContent=(i+1)+' / '+SLIDES.length;
  bar.style.width=((i+1)/SLIDES.length*100)+'%';
  if(!notesEl.hidden) showNotes();
  paintSpeaker();
  if(location.hash!=='#'+(i+1)) location.hash='#'+(i+1);
}
function toggleNotes(){ notesEl.hidden=!notesEl.hidden; if(!notesEl.hidden) showNotes(); }
function toggleFs(){ document.fullscreenElement ? document.exitFullscreen()
  : document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); }
// ---- Speaker view: a separate pop-up window (like reveal.js) showing the
// current slide, a preview of the next, the speaker notes, and a timer/clock.
// We fully own the pop-up (about:blank we write into), so it works over file://
// too. Navigation in either window stays in sync via the shared go().
let speaker=null, speakerStart=0;
function pad(n){ return (n<10?'0':'')+n; }
function speakerDoc(){ return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Speaker View</title>
<style>
  html,body{margin:0;height:100%;background:#0a0e1a;color:#dfe6f2;overflow:hidden;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;}
  #top{display:flex;align-items:baseline;gap:22px;padding:10px 16px;border-bottom:1px solid #223150;}
  #time{font:600 26px/1 ui-monospace,monospace;color:#6cf;cursor:pointer;user-select:none;}
  #clock{font:14px/1 ui-monospace,monospace;color:#8aa3c0;}
  #count{margin-left:auto;font:14px/1 ui-monospace,monospace;color:#8aa3c0;}
  #grid{display:flex;gap:14px;padding:14px 16px;height:46%;box-sizing:border-box;}
  .pane{position:relative;background:#000;border:1px solid #223150;border-radius:4px;overflow:hidden;}
  .pane img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;}
  .pane .lbl{position:absolute;top:6px;left:8px;z-index:1;font:600 11px/1 sans-serif;letter-spacing:.12em;
    text-transform:uppercase;color:#6cf;background:rgba(10,14,26,.75);padding:3px 6px;border-radius:3px;}
  #cur{flex:2;} #nxt{flex:1;}
  #notes{padding:16px 20px;height:calc(54% - 44px);box-sizing:border-box;overflow:auto;
    border-top:1px solid #223150;white-space:pre-wrap;font-size:20px;line-height:1.55;}
  #notes .empty{color:#56708f;font-style:italic;}
  #foot{position:fixed;bottom:6px;right:12px;font:12px/1 sans-serif;color:#56708f;}
</style></head><body>
  <div id="top"><span id="time" title="click to reset">0:00</span><span id="clock"></span><span id="count"></span></div>
  <div id="grid">
    <div class="pane" id="cur"><span class="lbl">Current</span><img id="curimg" alt=""></div>
    <div class="pane" id="nxt"><span class="lbl">Next</span><img id="nximg" alt=""></div>
  </div>
  <div id="notes"></div>
  <div id="foot">← → navigate · click timer to reset</div>
</body></html>`; }
function openSpeaker(){
  if(speaker && !speaker.closed){ speaker.focus(); return; }
  speaker=window.open('','pptx-speaker-view','width=1100,height=760');
  if(!speaker){ alert('Speaker view was blocked by your pop-up blocker. Allow pop-ups and press S again.'); return; }
  speaker.document.open(); speaker.document.write(speakerDoc()); speaker.document.close();
  speakerStart=Date.now();
  speaker.document.addEventListener('keydown',e=>{
    switch(e.key){
      case 'ArrowRight': case ' ': case 'PageDown': go(i+1); break;
      case 'ArrowLeft': case 'PageUp': go(i-1); break;
      case 'Home': go(0); break;
      case 'End': go(SLIDES.length-1); break;
      default: return;
    }
    e.preventDefault();
  });
  speaker.document.getElementById('time').addEventListener('click',()=>{ speakerStart=Date.now(); });
  speaker.setInterval(tickSpeaker,1000);     // owned by the pop-up; auto-stops when it closes
  paintSpeaker();
}
function tickSpeaker(){
  if(!(speaker && !speaker.closed)) return;
  const d=speaker.document, t=d.getElementById('time'); if(!t) return;
  const s=Math.floor((Date.now()-speakerStart)/1000);
  t.textContent=Math.floor(s/60)+':'+pad(s%60);
  const c=d.getElementById('clock'), now=new Date();
  if(c) c.textContent=pad(now.getHours())+':'+pad(now.getMinutes())+':'+pad(now.getSeconds());
}
function paintSpeaker(){
  if(!(speaker && !speaker.closed)) return;
  const d=speaker.document;
  const cur=d.getElementById('curimg'); if(cur) cur.src=SLIDES[i].img;
  const nx=d.getElementById('nximg');
  if(nx){ if(i+1<SLIDES.length){ nx.src=SLIDES[i+1].img; nx.style.display='block'; }
    else { nx.removeAttribute('src'); nx.style.display='none'; } }
  const nb=d.getElementById('notes');
  if(nb){ const txt=(NOTES[i]||'').trim();
    if(txt){ nb.textContent=txt; } else { nb.innerHTML='<span class="empty">(no notes for this slide)</span>'; } }
  const cnt=d.getElementById('count'); if(cnt) cnt.textContent='Slide '+(i+1)+' / '+SLIDES.length;
  tickSpeaker();
}
addEventListener('keydown',e=>{
  switch(e.key){
    case 'ArrowRight': case ' ': case 'PageDown': go(i+1); break;
    case 'ArrowLeft':  case 'PageUp':            go(i-1); break;
    case 'Home': go(0); break;
    case 'End':  go(SLIDES.length-1); break;
    case 's': case 'S': openSpeaker(); break;
    case 'n': case 'N': toggleNotes(); break;
    case 'f': case 'F': toggleFs(); break;
    case 'Escape': if(!notesEl.hidden) notesEl.hidden=true; else return; break;
    default: return;
  }
  e.preventDefault();
});
document.getElementById('stage').addEventListener('click',()=>go(i+1));
addEventListener('hashchange',()=>{ const n=hashIndex(); if(n!==i) go(n); });
// expose minimal API for automated verification
window.deck={get total(){return SLIDES.length}, get index(){return i}, go,
  get notesOpen(){return !notesEl.hidden}, get speakerOpen(){return !!(speaker&&!speaker.closed)},
  openSpeaker, notes:NOTES,
  images:SLIDES.map(s=>s.img), gifs:SLIDES.flatMap(s=>(s.gifs||[]).map(g=>g.src))};
addEventListener('beforeunload',()=>{ if(speaker && !speaker.closed) speaker.close(); });
go(hashIndex());
setTimeout(()=>hint.classList.add('gone'),4500);
</script>
</body>
</html>
"""


def main():
    argv = sys.argv[1:]
    if not argv:
        die('usage: python3 singlefile.py <build_dir> [output.html] [--quality N] [--format webp|png]')
    fmt, quality, pos = 'webp', 82, []
    i = 0
    while i < len(argv):
        if argv[i] == '--quality': quality = int(argv[i + 1]); i += 2
        elif argv[i] == '--format': fmt = argv[i + 1]; i += 2
        else: pos.append(argv[i]); i += 1
    build_dir = pos[0]
    slides_dir = os.path.join(build_dir, 'slides')
    if not os.path.isdir(slides_dir):
        die('no slides/ in %s (run pptx2html.py / build.sh first)' % build_dir)
    if fmt == 'webp' and not _have('magick'):
        die("ImageMagick 'magick' not found (needed for webp). Use --format png or `brew install imagemagick`.")
    out_html = pos[1] if len(pos) > 1 else os.path.abspath(build_dir).rstrip('/') + '.html'

    imgs = sorted(glob.glob(os.path.join(slides_dir, 'slide-*.png')),
                  key=lambda p: int(re.search(r'(\d+)\.png$', p).group(1)))
    if not imgs:
        die('no slide-*.png in ' + slides_dir)
    notes_map = json.load(open(os.path.join(build_dir, 'notes.json'))) \
        if os.path.exists(os.path.join(build_dir, 'notes.json')) else {}
    overlays_map = json.load(open(os.path.join(build_dir, 'overlays.json'))) \
        if os.path.exists(os.path.join(build_dir, 'overlays.json')) else {}

    gif_cache, n_gifs = {}, 0
    slides, notes_list = [], []
    for idx, png in enumerate(imgs, start=1):
        sys.stdout.write('\r  embedding slide %d/%d' % (idx, len(imgs))); sys.stdout.flush()
        gifs = []
        for g in overlays_map.get(str(idx), []):
            path = os.path.join(build_dir, g['file'])
            if not os.path.exists(path):
                continue
            if path not in gif_cache:
                gif_cache[path] = encode_gif(path)
            gifs.append({'src': gif_cache[path], 'left': g['left'], 'top': g['top'],
                         'w': g['w'], 'h': g['h']})
            n_gifs += 1
        slides.append({'img': encode_image(png, fmt, quality), 'gifs': gifs})
        notes_list.append(notes_map.get(str(idx), ''))
    print()

    title = read_title(build_dir)
    doc = (TEMPLATE
           .replace('__TITLE__', html.escape(title))
           .replace('__SLIDES__', json.dumps(slides))
           .replace('__NOTES__', json.dumps(notes_list, ensure_ascii=False)))
    with open(out_html, 'w') as f:
        f.write(doc)
    mb = os.path.getsize(out_html) / 1e6
    print('Wrote %s  (%.1f MB, %d slides, %d animated GIF(s), single file, no dependencies)'
          % (out_html, mb, len(imgs), n_gifs))


def _have(cmd):
    from shutil import which
    return which(cmd) is not None


if __name__ == '__main__':
    main()
