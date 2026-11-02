# Promptioo Gallery

Home page says **Welcome to Promptioo Gallery** with 5 tiles: Men, Women, Kids, Couples, Other.
Click a tile to see its prompts by category (Portrait, Photography, Cinematic...). Click an image to open it in the viewer with its prompt.

## Add prompts
Put CSV files in the category folders. **The file name is the category tab.**

    data/men/portrait.csv        -> Men > Portrait
    data/men/cinematic.csv       -> Men > Cinematic
    data/women/photography.csv   -> Women > Photography
    (also data/kids/, data/couples/, data/other/)

Columns (first row is the header): `title,prompt,keywords,image_urls`

- `keywords`: separate with `|` or `,`
- `image_urls`: one URL, or several separated by `|` (the viewer shows them as thumbnails)
- Wrap `prompt` in double quotes if it has commas or line breaks
- Optional `subcategory` column overrides the file name for that row

## Big CSVs? The workflow splits them for you
`scripts/build.py` runs in GitHub Actions and splits every CSV automatically, so visitors never download a whole CSV:

- listing pages of 60 images per tab (`data/men/portrait-1.json`, `-2.json`, ...), loaded as you scroll
- prompt details in files of 200 (`data/men/items/0.json`), loaded only when an image is opened
- a search file that loads only when someone types in the search box

Tested with 30,000 prompts in one category. To run it by hand: GitHub repo > Actions > "Split CSVs and deploy gallery" > Run workflow.

## Publish on GitHub Pages
1. Upload this whole folder (including the hidden `.github` folder) to a repo on the `main` branch.
2. Settings > Pages > Source: **GitHub Actions**.
3. Every time you add or change a CSV, the site rebuilds. Check the Actions tab for a green tick.

## Test on your computer
    python3 scripts/build.py
    cd _site && python3 -m http.server

Open http://localhost:8000 (opening the files directly will not work, the pages load data files).
