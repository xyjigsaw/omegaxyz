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

The generated site is written to `docs/`, so GitHub Pages can serve it from the `main` branch `/docs` folder.

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
