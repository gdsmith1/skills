# Photographic scenery pipeline (Tier 3)

Only use this tier if the user wants photographic fidelity. Everything here was done in a real project (a dashboard emitted as one self-contained HTML file, desktop only). Scripts lived in a scratchpad; re-create them from these patterns.

## Licensing rules
- Only **CC0, Public domain, or US-government** works. No CC-BY/BY-SA (no in-page attribution mechanism in a single file), never NC/ND. Accept only the exact strings `CC0` and `Public domain` in `LicenseShortName`; "No restrictions" (Internet Archive scans) is not acceptable.
- Good sources: NASA (Blue Marble), NOAA National Marine Sanctuaries (dolphin, turtle, jellyfish), US Fish & Wildlife (plants, birds), USDA, and individual CC0 Commons uploaders (clouds, textures, skylines).
- Keep `img/MANIFEST.md` (size, description, layout notes) and `img/CREDITS.md` (Commons title, author, licence, processing) and update both on add/delete. Add a test that every image file appears in CREDITS. Look up the real author via `extmetadata`; do not guess.
- Procedural assets (hills, tiles) are flagged as procedural in CREDITS.

## Searching Wikimedia Commons
Always send a descriptive User-Agent. Search and licence-check in one call:
```python
import json, urllib.request, urllib.parse
UA={'User-Agent':'my-asset-tool/1.0'}
def api(**p):
    p['format']='json'
    u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA)))
r=api(action='query',generator='search',gsrsearch=q+' filetype:bitmap',gsrnamespace=6,gsrlimit=12,
      prop='imageinfo',iiprop='extmetadata|size',iiextmetadatafilter='LicenseShortName|Artist')
```
Print `title | w h | licence | artist`; keep only CC0/PD. Adding "CC0", "Public domain" or "NASA" to the query helps. Download a scaled thumb with `iiurlwidth=<W>` (`thumburl`), not the original. Expect HTTP 429: sleep 2-8 s between calls, verify downloads with `magick identify` (a 429 body is HTML), include an index/hash in saved filenames (truncated names collide). Triage with `magick montage a.jpg b.jpg -tile 5x -geometry 380x280+4+4 sheet.jpg`.

Queries that found keepers: "cumulus congestus blue sky CC0", "Blue Marble NASA Earth", "seamless lawn grass texture", "glass skyscrapers blue sky CC0", "green sea turtle swimming", "jellyfish NOAA", "Wave splash ... CC0".

## Tooling
`uv venv --python 3.11` then `uv pip install "rembg[cpu]" onnxruntime pillow numpy scipy` (rembg needs Python <= 3.12). ImageMagick for montage/crop/identify. Run python with `-I` on untrusted downloads. Write WebP with Pillow: `im.save(p,'WEBP',quality=Q,method=6,alpha_quality=90)`.

## Cutout helpers
- `largest(alpha)`: keep the biggest connected component. `bbox_crop(pad)`.
- `clean_alpha`: erode 1, gaussian feather ~.8, contrast `clip((a-.08)/.84)` (halo removal).
- `defringe`: un-premultiply old bg `(rgb - bg*(1-a))/max(a,.35)`.
- `rim`: 1px light rim from `alpha - eroded alpha` mixed in at .15-.35.
- `resize_w`: **premultiplied** LANCZOS resize then un-premultiply (prevents dark halos).
- **Always preview on `#0aa0e0`**: `magick -size 700x500 xc:'#0aa0e0' \( cut.png -resize 700x500 \) -gravity center -composite p.png`. Halos only show on the real background.

## Recipes by subject
- **Wildlife/aircraft**: `rembg` (`isnet-general-use`; `birefnet-general-lite` for fine filaments). Crop first for small subjects. Fish keep background coral: check the lower edge. Colour-correct by HSV; view after each hue change (a wrong shift turned a meadow orange).
- **Clouds**: rembg is poor. Key on saturation: `alpha = 1 - smoothstep(sat, lo, hi)` (Sky saturated, cloud near neutral; lo/hi ~.11/.22 for pale skies, ~.25/.62 for deep blue). Fade alpha near crop edges (`clip(dist_to_edge/fade,0,1)`), pull colour 65% toward luminance to kill blue spill, tint lower half toward `[.52,.66,.88]` for a blue-grey underside. Width 800-1400, q82. Cirrus: use SVG feTurbulence instead of photos.
- **Hills**: photo hills never looked right (skies, clutter). Use rendered layers: sum-of-sines ridge, shading from ridge slope (sun top-left), crest glow, depth darkening, blade-level texture, haze only on the far layer, three layers (far/mid/near) at ~3200x700.
- **Skyline**: threshold sky out, keep components touching the bottom, defringe, tint toward cyan; composite glass over a dark navy so towers are opaque.
- **Water tile**: crop square to 512, `np.roll` by 256 on both axes and blend with a centre mask to hide seams, grade luminance into `#0090d0 -> #00b8e6 -> #9ef2ff`, opaque WebP q84; tile 2x2 to check seams.
- **Globe**: NASA Blue Marble, circular alpha, saturation x1.55, gamma .62; add gloss in CSS.
- **Splash/spray**: macro photos and generated sprites failed. A CC0 wave-splash photo with white spray over a dark sea worked, keyed by whiteness not rembg: `alpha=smoothstep(min(R,G,B),.60,.88)*(1-smoothstep(sat,.20,.42))`, tinted aqua with a cyan underlay, edge-faded.
- **Monitor with splash (hero object)**: public-domain monitor cutout, screen replaced by a perspective-warped landscape (`Image.transform(...PERSPECTIVE...)`, 8x8 `np.linalg.solve` from four corners), recoloured to site palette; spray and fish as separate layers on one 780x795 canvas, fish between them; one 9 s event with complementary keyframes; reduced-motion shows the still pose.

## Size budget
Aim for ~2 MB of WebP total (~3 MB as base64 in the HTML). Wildlife/clouds q82-85 at 560-900 px; hills 2200+ wide q70; font ~16 KB each. Tighten before adding a big file.

## Single-file inlining
Reference each image **exactly once** in CSS as a custom property on a lane root (`.aero-sky{--c1:url(img/aero_cloud_1.webp)}`) and use `background-image:var(--c1)` elsewhere; per-selector `url()` would duplicate the base64 (one project dropped 5.7 MB to 3.2 MB by de-duplicating). A render step replaces `url(img/x)` and `url(fonts/x.woff2)` with data URIs and should fail loudly on a missing file. Do not use `<img src>` for scenery. Share image variables across lanes via a grouped selector.

## Lane ownership for parallel agents
Split into lanes with exclusive files (sky, hero/hills, water, animals, bubbles, ui, polish). Later stylesheets win; give each lane its own `.css` + optional `.html` fragment injected at a `<!--SCENE:lane-->` marker.
