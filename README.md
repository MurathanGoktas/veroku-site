# Ghisa-Verioku

The Veroku website (veroku.net). It started as a static copy of https://earendil.com (mirrored 2026-11-02); the theme is still theirs, credited in the black banner at the bottom of every page.

## Run locally

All asset and page links are root-relative (`/static/...`), so serve `site/` as the web root rather than opening the HTML files directly:

```bash
python3 serve.py
```

Then open http://localhost:8000. `serve.py` serves `site/` with `Cache-Control: no-store`, so a normal reload always shows the latest edits (including the `locales/*.json` text). Pass a port to use another one: `python3 serve.py 8080`.

## Deploy

GitHub Pages serves the `gh-pages` branch of [MurathanGoktas/veroku-site](https://github.com/MurathanGoktas/veroku-site) at https://veroku.net. That branch is the `site/` folder on its own, split off `main`. After committing to `main`, publish with:

```bash
git push origin main
git push --force origin "$(git subtree split --prefix site)":gh-pages
```

`gh-pages` is generated from `site/`, so it is force-pushed: when the domain is changed in the GitHub Pages settings, GitHub commits its own `CNAME` edits to that branch, and the next push replaces them.

Pushes go through the MurathanGoktas GitHub account (`gh auth switch -u MurathanGoktas` if gh is on another account). HTTPS is on (GitHub's certificate, renewed automatically). DNS for veroku.net is at GoDaddy: four A records to GitHub Pages (185.199.108-111.153) and `www` as a CNAME to `murathangoktas.github.io`.

## Layout

```
site/
  index.html                 home (slogan)
  purpose/                   Mission page (nav label "Mission" / "Misyon")
  values/                    Values and Operating Principles
  projects/                  Projects (placeholder text for now)
  writing/                   Writing (placeholder text for now)
  join/                      Join Us (placeholder text for now)
  404.html                   not-found page
  CNAME                      GitHub Pages domain (veroku.net)
  locales/tr|en/*.json       i18n strings (Turkish and English x common, errors, content), loaded by static/i18n.js
  static/
    styles.css               all styles, including the credit banner at the end
    script.js                ocean canvas background, menu, theme toggle
    i18n.js                  translation loader
    htmx-bundle.min.js       page transitions (hx-boost swaps div.page)
    purify.min.js            DOMPurify, sanitizes translated HTML
    veroku-mark.svg          site logo: the eye-shaped "o" symbol in white (CSS tints it); also drawn by the canvas
    favicon/                 favicons and app icons drawn from the same symbol
    fonts/                   Departure Mono and Commit Mono (both free, OFL)
brand/                       logo files: veroku-logo.svg/.png (wordmark), veroku-symbol.svg/.png (the "o"),
                             verioku-logo-original.png (the old name's logo they were traced from)
earendil-arsiv/              everything removed before publishing (not part of the site, gitignored)
```

## Editing the page text

The text of the Mission, Values (with Operating Principles), Projects, Writing and Join Us pages lives in `site-text.json` (Turkish and English, each item with a short explanation that opens when the item is clicked on the site). Edit it in the browser at http://localhost:8000/_edit/ while `serve.py` runs: saving writes `site-text.json` and rebuilds those pages and the `content.*` keys in `locales/en` and `locales/tr` (`sitetext.py`). The editor only answers on this computer and is not part of `site/`, so it is never published. Running `python3 sitetext.py` does the same rebuild from the file. Run it after editing anything in `locales/tr/` too, so the Turkish HTML picks it up (see Text).

## Text

The site is Turkish and English only, Turkish by default (`DEFAULT_LANG` in `static/i18n.js` and `sitetext.py`); a visitor's choice is kept in the `lang` cookie. The pages' HTML is written in Turkish by `sitetext.py` from `locales/tr/`, so a page reads right before the translations load and without JavaScript; choosing English swaps in `locales/en/`. Strings missing in Turkish fall back to English. Where our text lives:
- Home slogan: `home.tagline` in `common.json`
- Mission, Values, Operating Principles, Projects, Writing, Join Us: generated from `site-text.json` (see above) into `mission.*`, `values.list.*`, `values.principles.*`, `projects.*`, `writing.*`, `join.*` and the headings in `content.json`; explanations use the item key plus `.desc`

The page `<meta>` descriptions are the Turkish slogan. The other 25 languages of the original theme were removed (they are in the git history).

## Removed before publishing

Moved to `earendil-arsiv/` with their original paths: Earendil's posts and feeds, the Join and Subscribe pages, post media, KaTeX, the asciinema player, `prose.css`, the Earendil logo and favicons, the Plantin font (licensed to Earendil), and the posts/subscribe locale files. Links to those pages, Earendil's external project links, the newsletter form code and unused Earendil text in the locale files are gone. The serif text now uses Georgia.

## Still to do

- The theme (styles, scripts, ocean canvas) is Earendil's; their site repo has no license, so ask them for permission or replace it over time.
- The 404 message ("It was lost, and has not been seen again.") is still Earendil's wording.
