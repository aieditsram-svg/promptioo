# Ai Edits Ram – your gallery + your viewer, driven by a CSV

The site uses YOUR original two pages as templates, so the design, ocean animations, side menu, blog promo slider and ads stay exactly as you made them.

## 1. Add your two original files (one time)
- Paste your **gallery code** (Glassmorphic Ocean Grid) into `templates/gallery.html`
- Paste your **viewer code** (prompt card with promo + ads) into `templates/viewer.html`
Paste them unchanged. The build fills in the menu tabs, images and prompts for you.

## 2. Fill data/prompts.csv
Header row: `title, prompt, category, subcategory, keywords, image_urls`
- **category**: Men, Women, Kids, Couples or Others (anything else goes to Others)
- **subcategory**: the tabs on that category's page, e.g. Portrait, Photography, Cinematic, Fantasy
- **keywords**: separate with `|` or `,`
- **image_urls**: one URL, or several separated by `|` (each becomes a slide in the viewer)
- Wrap `prompt` in double quotes if it contains commas or line breaks
- Add new rows at the bottom (links use the row number)

## What gets built
- `index.html` – the 5 categories
- `men.html`, `women.html`, … – category pages (your gallery design, one tab per subcategory)
- `men-portrait.html`, … – each subcategory (400 images per page; larger ones continue as "Portrait 2", "Portrait 3")
- `viewer.html?id=123` – your viewer, loading prompt 123. Its keyword links and its "related posts" drawer use the CSV (prompts that share keywords), not Blogger.
- `search.html?q=word` – search results in your gallery design (title, keywords, category), 400 per page. The search box on every gallery page goes here too.

## Publish on GitHub (rebuilds automatically)
1. Upload everything in this folder to a new repo.
2. **Add file → Create new file**, name it `.github/workflows/deploy.yml`, paste the contents of `deploy-workflow.yml`, commit.
3. **Settings → Pages → Source: GitHub Actions**.
4. After every change to the CSV or templates, check the **Actions** tab; a green tick means the site is live.

## Test on your computer
```
python3 scripts/build.py
cd _site && python3 -m http.server
```
Open http://localhost:8000
