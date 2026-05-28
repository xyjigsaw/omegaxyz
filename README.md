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

The generated site is written to `docs/`. The current public site is published by copying `docs/` to the `gh-pages` branch.

## GitHub Pages Publishing

The site can be published in either of these ways:

1. Current mode: use the `gh-pages` branch. Build locally, copy `docs/` to `gh-pages`, and push that branch.
2. GitHub Actions mode: in GitHub, open `Settings -> Pages -> Build and deployment`, set `Source` to `GitHub Actions`, then add a Pages workflow that uploads the `docs/` folder.

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

## Custom Domain Later

When `omegaxyz.com` is ready to move to GitHub Pages, copy `CNAME.example` to `docs/CNAME`, rebuild, commit, and configure the custom domain in the GitHub Pages settings.
