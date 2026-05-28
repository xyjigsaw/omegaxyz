# OmegaXYZ Static Site

This repository contains a GitHub Pages-ready static migration of the former WordPress site.

## Build

```bash
python3 scripts/migrate_wordpress.py \
  --backup-dir .. \
  --output data/site.notranslate.json \
  --extract-media .media/uploads

python3 scripts/translate_site.py --workers 8
python3 scripts/build_site.py
```

The generated site is written to `docs/`. The current public site is deployed by GitHub Actions from the `master` branch.

## GitHub Pages Publishing

The site is set up for GitHub Actions mode. In GitHub, open `Settings -> Pages -> Build and deployment`, set `Source` to `GitHub Actions`, and keep the workflow that uploads the `docs/` folder.

Minimal workflow for Actions mode:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs
      - id: deployment
        uses: actions/deploy-pages@v4
```

If `Source` is still set to a branch instead of `GitHub Actions`, this workflow will fail at the Pages configuration step.

## Media Upload

Images and other uploaded WordPress media are rewritten to `https://cdn.omegaxyz.com/...`.
Upload extracted files to Cloudflare R2 with:

```bash
python3 scripts/upload_r2.py \
  --root .media/uploads/uploads \
  --account-id "$CF_ACCOUNT_ID" \
  --bucket omegaxyz-image
```

Set `CF_API_TOKEN` and `CF_ACCOUNT_ID` in your shell before running the upload command.
The script stores progress in `.cache/r2-uploaded.json` and can be resumed.
Do not commit Cloudflare tokens, account IDs, S3 credentials, or generated migration caches.

## Custom Domain

The generated site writes `docs/CNAME` with `omegaxyz.com`, and generated metadata uses `https://omegaxyz.com` for canonical URLs, Open Graph URLs, `robots.txt`, and `sitemap.xml`.

To finish the domain switch in GitHub Pages, set the custom domain to `omegaxyz.com` and point DNS to GitHub Pages. Keep `cdn.omegaxyz.com` on Cloudflare R2 for uploaded media.
