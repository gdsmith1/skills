# CSS recipes (verified in a real dashboard restyle)

Load as the last stylesheet. Tokens first.

```css
:root{
  --fa-sky-1:#0a4fb4; --fa-sky-2:#2fb4f0; --fa-sky-3:#bff0ff;
  --fa-ink:#08305e;
  --fa-glass:rgba(236,248,255,.30);
  --fa-r:18px;
  --fa-gel: linear-gradient(to bottom,#73c8f8 0%,#1583d7 50%,#0361A3 50%,#299eef 100%);
  --fa-gel-green: linear-gradient(to bottom,#c8f78c 0%,#4fd22c 50%,#1f8f12 50%,#58e03a 100%);
  --fa-gel-sun: linear-gradient(to bottom,#fff0a0 0%,#ffc21a 50%,#e08a00 50%,#ffd24a 100%);
}
body{
  color:var(--fa-ink);
  background:linear-gradient(160deg,var(--fa-sky-1),var(--fa-sky-2) 55%,var(--fa-sky-3)) fixed;
  font-family:"Segoe UI","Open Sans Aero","Open Sans",system-ui,sans-serif;
}
```

## Glass panel (cards, stats, drawers, tooltips)
```css
.card{
  background-color:rgba(236,248,255,.30);
  background-image:linear-gradient(160deg,rgba(255,255,255,.62) 0,rgba(255,255,255,.18) 30%,rgba(255,255,255,0) 45%);
  backdrop-filter:blur(20px) saturate(1.45) brightness(1.12);
  border:1px solid rgba(255,255,255,.8);
  border-bottom-color:rgba(10,70,130,.28);
  border-radius:var(--fa-r);
  box-shadow:0 0 0 1px rgba(0,60,110,.28),0 10px 20px rgba(0,0,0,.1),0 2px 4px rgba(0,50,100,.25),
    0 0 16px rgba(0,200,255,.22),inset 0 1px 0 #fff,inset 0 0 0 1px rgba(255,255,255,.55),inset 0 -1px 0 rgba(0,40,90,.25);
  text-shadow:0 0 3px rgba(255,255,255,.9),0 0 9px rgba(255,255,255,.55);
}
```
- `brightness(1.12)` in the backdrop filter is what washes grass and noise out behind small text; blur alone is not enough.
- Nested panels: reset the inner one to no background so glass is not doubled.
- Text directly on the scene (subtitles, standalone labels, bars): give it its own small glass backing (`rgba(236,248,255,.34)`, `blur(12px) brightness(1.1)`, radius 14px).
- Wrap in `@supports not (backdrop-filter:blur(1px)){...}` with a more opaque fill (~.75).
- Do not add hover `transform` lifts to many backdrop-filter cards (cost and flicker).

## Card title strip (Windows 7 window feel)
Pale blue gradient header at ~.82 alpha, glossy top. Do not add fake close/min/max buttons unless they work.

## Gel button
```css
.btn{
  background:var(--fa-gel); color:#fff; text-shadow:0 -1px 0 rgba(0,40,90,.5);
  border:1px solid #0a4a86; border-radius:999px; padding:.45em 1.1em; font-weight:600;
  box-shadow:inset 0 1px 1px rgba(255,255,255,.85),inset 0 15px 15px rgba(255,255,255,.3),
    0 4px 6px rgba(0,0,0,.2),0 3px 8px rgba(0,150,255,.45);
}
.btn:hover{filter:brightness(1.12) saturate(1.15)}
.btn.go{background:var(--fa-gel-green)} .btn.warn{background:var(--fa-gel-sun);color:#5a3a00;text-shadow:0 1px 0 rgba(255,255,255,.6)}
@media (prefers-reduced-motion:no-preference){
  .btn::after{content:"";position:absolute;inset:0;border-radius:inherit;pointer-events:none;
    background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.75) 50%,transparent 65%) 160% 0/250% 100% no-repeat;transition:background-position .6s}
  .btn:hover::after{background-position:-60% 0}
}
.btn{position:relative;overflow:hidden}
```
Use green for primary/confirm, sun yellow for warnings, blue default.

## Inputs, tabs, checkboxes, scrollbars
- Inputs: inset white-to-pale gradient, 1px `#7aa7cf` border, inset shadow, cyan focus ring `0 0 0 3px rgba(0,200,255,.45)`.
- Tabs/nav: glossy pill; active tab uses the gel gradient. A bottom taskbar dock (62px, two-band gradient with the same 49%/51% hard split, `backdrop-filter:blur(14px) saturate(1.5)`, green start orb) works well for tab navigation; add body bottom padding so it never covers content.
- Scrollbars: `::-webkit-scrollbar` with glass track and gel thumb, plus `scrollbar-color` fallback.
- Checkboxes: custom `appearance:none` gel squares with a tick.

## Headings
h1: white, cyan glow `0 0 12px rgba(0,220,255,.8)`, optional `-webkit-box-reflect: below -2px linear-gradient(transparent 60%,rgba(255,255,255,.3))` on each stat/card rather than a whole row. h2: glossy capsule with a coloured icon tile cycling five colours via `:nth-of-type`.

## Bubbles (CSS only)
```css
.bubble{position:fixed;border-radius:50%;pointer-events:none;
  background:radial-gradient(circle at 30% 25%,rgba(255,255,255,.95) 0 6%,rgba(255,255,255,.1) 30%,rgba(120,220,255,.12) 60%,rgba(255,255,255,.55) 100%);
  box-shadow:inset 0 0 12px rgba(255,255,255,.6),0 0 14px rgba(0,200,255,.3);
  animation:rise var(--t,18s) linear infinite, wob 4s ease-in-out infinite alternate}
@keyframes rise{from{translate:0 110vh}to{translate:0 -20vh}}
@keyframes wob{from{margin-left:-9px}to{margin-left:9px}}
```
Vary size/delay with nth-child. Thin-film variant: add a faint conic-gradient of pink/cyan/yellow at low alpha.

## Scenery without photos (Tier 2)
- Sun: radial gradient top-left plus a few ghost circles along a diagonal for lens flare; conic-gradient rays at low alpha, slowly rotating (opacity/rotate only).
- Clouds: blurred white ellipses via radial gradients, or SVG `feTurbulence` + `feDisplacementMap`; drift with `translate` over 70-120s `ease-in-out infinite alternate` and negative delays.
- Hills: two or three layers, each an SVG path or clip-path ridge with lime gradient; mirror and offset layers so ridges cross and sky shows between.
- Water band: bottom aqua gradient, caustic overlay via repeating radial gradients, a wave crest SVG.
- Cirrus: SVG `feTurbulence` (baseFrequency ~.004 .02) with alpha threshold, stretched horizontally.

## Layer / z-index plan
sky 0, hills 1, water 2, back bubbles 4, animals 8, foliage 9, content column 10, front bubbles 20, dock 60, overlays 150+. All scene layers `position:fixed; inset:0; pointer-events:none; overflow:hidden`. Animals behind the glass show blurred through it, which reads as depth; in front of text they read as stickers.

## Animation and performance
- Animate only `translate`, `rotate`, `scale`, `opacity`. Blur static layers; animate their opacity.
- Few fixed layers; use `mask-image` for soft edges.
- `@media (prefers-reduced-motion:reduce){.scene *{animation:none!important}}` and park moving objects at a pleasant rest pose.
- `@media (prefers-contrast:more),(forced-colors:active){.scene{display:none}}` plus opaque panels.
- Never: scroll-linked scenery, mouse parallax, `mix-blend-mode` overlays that move under backdrop-filter cards, per-pointermove custom-property writes on `:root`. These caused visible flicker.
- When deleting selectors from a grouped rule, check for a dangling comma (`.a,.b,{}` silently invalidates the rule).
- CSS specificity trap: a shorthand `background:` on a more specific selector can wipe a `background-image` set elsewhere; keep image properties on the same selector.

## Fonts
Bundle Open Sans (latin 400/600/700 woff2, ~16 KB each, OFL) if the page must work offline, via `@font-face` and a local file; otherwise rely on `"Segoe UI"` with system fallbacks.
