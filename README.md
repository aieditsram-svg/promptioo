# Ai Edits Ram – CSV-driven gallery

Static site (no build step) for GitHub Pages. All content comes from `data/prompts.csv`.

## CSV columns (header row required)
`title, prompt, category, keywords, image_urls`
- **category**: one of `Men`, `Women`, `Kids`, `Couples`, `Others` (any other value is placed in Others)
- **keywords**: separate with `|` or `,` (wrap the cell in quotes if you use commas)
- **image_urls**: one URL, or several separated by `|` (extra images show as thumbnails in the viewer; the first is the gallery cover)
- Wrap `prompt` in double quotes if it has commas or line breaks; write a literal quote as `""`
- Optional `id` column for stable links; otherwise the id is made from the title

## Pages
- `index.html` – all categories (a section each), `?q=word` for search
- `category.html?cat=Men` – dedicated category page listing every prompt in that category (Grid or List view, with in-category search)
- `viewer.html?id=...` – opens when you click an image

## Test locally
`python3 -m http.server` then open http://localhost:8000 (opening the file directly will not load the CSV)

## Publish
Push to GitHub, then Settings → Pages → Deploy from branch → main → / (root).
