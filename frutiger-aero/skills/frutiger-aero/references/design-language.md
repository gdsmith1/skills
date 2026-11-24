# Frutiger Aero design language

## What it is
A visual style of roughly 2004-2013, centred on Windows Vista/7 (Aero Glass), Apple's Aqua-era skeuomorphism, and mid-2000s Sony/Nokia/Samsung/Wii-era product and stock imagery. It succeeded Y2K chrome and gave way to flat design (Windows 8, iOS 7). The name (coined ~2017-18 by Sofi Lee) joins the Frutiger typeface with Windows Aero. It resurged online around 2023 as nostalgia; Apple's 2025 "Liquid Glass" is often compared to it. Some sources conflict on exact dates; do not state them as settled.

Mood: optimistic, clean, human-friendly technology; nature softens the machine.

## Core traits (consistent across sources)
- **Glossy, wet, lacquered surfaces**: buttons, icons and panels with specular highlight strips across the upper half.
- **Aero Glass**: frosted semi-transparent panels, blur, soft light diffusion, bright window borders.
- **Skeuomorphism and depth**: rounded corners, bevels, drop shadows, reflections, 3D feel. Depth gave hierarchy without explanation.
- **Nature imagery**: blue sky, clouds, lush grass hills, water, fish, dolphins, butterflies, dew, bubbles, sunrays, bokeh.
- **Bright, saturated colour**: cobalt, azure, cyan, aqua, lime, leaf green, sun yellow, clean white. Tertiary colours rather than neutrals.
- **Light effects**: lens flare, sun bloom and rays, glows around controls, caustics on water, thin-film iridescent bubbles.
- **Typography**: humanist sans (Frutiger, Segoe UI, Open Sans, Myriad, Lucida Grande, Trebuchet). Dark navy text on glass; white with a glow on headings over scenery.
- **Stock-photo world**: globes, handshakes, people with headsets in bright offices, glass skyscrapers, planes climbing through sky. Useful as scenery motifs.

## Sub-styles (pick one dominant)
- **Frutiger Aqua**: water, glass, cool blues, bubbles, fish.
- **Frutiger Eco**: green, grass, leaves, dew, natural textures.
- **Frutiger Metro / Technozen**: cleaner, more minimal, mixes with early flat design.

## Palette (starting tokens; tune per app)
| Role | Value |
|---|---|
| Sky top / bottom | `#0a4fb4` (cobalt) to `#2fb4f0` to `#bff0ff` (horizon haze) |
| Water | `#0090d0`, `#00b8e6`, `#9ef2ff` |
| Grass | deep `#1c8a0f`, mid `#3fc21f`, light `#b6f56a`, rim light `#d8ff8a` |
| Sun / warning | `#fff0a0`, `#ffc21a`, `#e08a00` |
| Glass fill | `rgba(236,248,255,.30)` over scenery, border `rgba(255,255,255,.8)` |
| Text | navy `#08305e` body, `#ffffff` + cyan glow for headings on scene |
| Accent gel blue | `#73c8f8 / #1583d7 / #0361A3 / #299eef` |

## How it differs from neighbours
- **Glassmorphism** (2020s): flat translucent cards, muted gradients. Frutiger Aero adds gloss, gel buttons, nature scenery and saturated colour. If your result is "frosted cards on a purple gradient", it is not Aero.
- **Y2K**: metallic chrome, silver, techno-futurism, pinks and neons. Aero is natural blues and greens.
- **Flat/Metro/Material**: no depth or gloss. Opposite end.
- **Apple Aqua**: shares gel and droplets; Aero is more about glass, sky and nature.

## Critique checklist (use for audits)
1. Is there visible sky with sun glow and clouds, and hills and water that persist while scrolling?
2. Do panels show the scene blurred through them (translucent), not opaque?
3. Do buttons have the hard 50% split, top gloss and coloured glow?
4. Are there bubbles with specular highlights and some wildlife or nature accent?
5. Is colour saturated cobalt/cyan/lime with a warm sun accent, no muddy greys?
6. Do headings have glow/reflection; do cards have a title strip or glossy header?
7. Is text legible everywhere (contrast over clouds/grass)?
8. Does the layout still behave exactly as before?

## Sources consulted
Wikipedia "Frutiger Aero"; Aesthetics Wiki (fandom); Adobe Express, Kittl, Dazed, UWaterloo Computer Museum, daisyUI trends, Frutiger Aero Archive and assorted design guides. Most are blogs and fan wikis; treat precise CSS numbers there as suggestions and prefer values in `css-recipes.md` that were built and screenshot-verified in a real project.

## Motif vocabulary
The full catalogue of scenery, props, effects and chrome lives in `motifs.json` (picked at random by `scripts/pick_motifs.py`). The motifs the first hand-built example happened to use (skyline, birds, dolphin, monitor, globe, plane) are just six of 90+; do not treat them as the style's definition.
