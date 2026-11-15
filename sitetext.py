"""Build the Mission, Values, Projects, Writing and Join Us pages from site-text.json.

site-text.json holds the text of those pages in Turkish and English: a heading and
items, each item with an optional explanation that opens when the item is clicked.
This writes it into the English and Turkish locale files and into the pages' HTML
(English, so the pages read correctly before translations load).

Usage: python3 sitetext.py      (serve.py's editor at /_edit/ also calls build())
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
TEXT = ROOT / "site-text.json"

# section -> (heading key, item key prefix, English context for items)
SECTIONS = {
    "mission": ("mission.heading", "mission.", "Mission page paragraph"),
    "values": ("values.heading.main", "values.list.", "Values page list item"),
    "principles": ("values.heading.ops", "values.principles.", "Values page, Operating Principles list item"),
    "projects": ("projects.heading", "projects.", "Projects page paragraph"),
    "writing": ("writing.heading", "writing.", "Writing page paragraph"),
    "join": ("join.heading", "join.", "Join Us page paragraph"),
}
# Pages that are a heading followed by paragraphs: section -> page file under site/.
PARAGRAPH_PAGES = {
    "mission": "purpose/index.html",
    "projects": "projects/index.html",
    "writing": "writing/index.html",
    "join": "join/index.html",
}
HEADING_CONTEXT = {
    "mission": "Heading of the mission page",
    "values": "Values page main heading",
    "principles": "Values page second major heading",
    "projects": "Heading of the projects page",
    "writing": "Heading of the writing page",
    "join": "Heading of the join us page",
}
OWNED_PREFIXES = tuple(prefix for _, prefix, _ in SECTIONS.values())
ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9]{0,39}$")


def validate(data):
    """Raise ValueError with a readable message if the text can't be built."""
    if not isinstance(data, dict) or set(data) != set(SECTIONS):
        raise ValueError("Expected the sections: " + ", ".join(SECTIONS))
    for name, section in data.items():
        heading = section.get("heading") or {}
        for lang in ("tr", "en"):
            if not str(heading.get(lang, "")).strip():
                raise ValueError(f"{name}: heading ({lang}) is empty")
        ids = set()
        for n, item in enumerate(section.get("items") or [], 1):
            item_id = item.get("id", "")
            if not ID_PATTERN.match(item_id) or SECTIONS[name][1] + item_id == SECTIONS[name][0]:
                raise ValueError(f"{name} item {n}: bad id {item_id!r}")
            if item_id in ids:
                raise ValueError(f"{name}: id {item_id!r} is used twice")
            ids.add(item_id)
            for field in ("tr", "en"):
                if not str(item.get(field, "")).strip():
                    raise ValueError(f"{name} item {n}: text ({field}) is empty")
            for field in ("desc_tr", "desc_en"):
                if not isinstance(item.get(field, ""), str):
                    raise ValueError(f"{name} item {n}: {field} must be text")


def clean(text):
    return " ".join(str(text).split())


def esc(text):
    return html.escape(clean(text), quote=False)


def item_html(key, item, block):
    """One item: plain if it has no explanation, otherwise a <details> that opens to it."""
    text, desc = item["en"], clean(item.get("desc_en", "")) or clean(item.get("desc_tr", ""))
    if not desc:
        return (f'<p data-i18n="content.{key}">{esc(text)}</p>' if block
                else f'  <li data-i18n="content.{key}">{esc(text)}</li>')
    inner = (f'<details class="item-more"><summary data-i18n="content.{key}">{esc(text)}</summary>'
             f'<p data-i18n="content.{key}.desc">{esc(desc)}</p></details>')
    return inner if block else f"  <li>{inner}</li>"


def heading_html(key, text, spaced=False):
    cls = "section-heading section-heading--spaced" if spaced else "section-heading"
    return f'        <p class="{cls}"><em><strong data-i18n="content.{key}">{esc(text)}</strong></em></p>\n'


def section_list(data, name):
    _, prefix, _ = SECTIONS[name]
    items = "\n".join(item_html(prefix + i["id"], i, block=False) for i in data[name]["items"])
    return '<ul class="icon-list icon-list--star">\n' + items + ("\n" if items else "") + "</ul>\n"


def replace_letter_body(path, body):
    page = path.read_text()
    page, n = re.subn(r'(<div class="letter-body">\n).*?(      </div>\n    </article>)',
                      lambda m: m.group(1) + body + m.group(2), page, flags=re.S)
    if n != 1:
        raise RuntimeError(f"letter-body not found in {path}")
    path.write_text(page)


def build(data=None):
    if data is None:
        data = json.loads(TEXT.read_text())
    validate(data)

    # Locale files: drop the keys this file owns, then write them fresh.
    en_path, tr_path = SITE / "locales/en/content.json", SITE / "locales/tr/content.json"
    en, tr = json.loads(en_path.read_text()), json.loads(tr_path.read_text())
    owned = lambda k: k.startswith(OWNED_PREFIXES)
    en = {k: v for k, v in en.items() if not owned(k)}
    tr = {k: v for k, v in tr.items() if not owned(k)}
    for name, (heading_key, prefix, context) in SECTIONS.items():
        section = data[name]
        en[heading_key] = {"message": clean(section["heading"]["en"]), "context": HEADING_CONTEXT[name]}
        tr[heading_key] = clean(section["heading"]["tr"])
        for item in section["items"]:
            key = prefix + item["id"]
            en[key] = {"message": clean(item["en"]), "context": context}
            tr[key] = clean(item["tr"])
            desc_en, desc_tr = clean(item.get("desc_en", "")), clean(item.get("desc_tr", ""))
            if desc_en or desc_tr:
                en[key + ".desc"] = {"message": desc_en or desc_tr,
                                     "context": context + ": explanation shown when the item is clicked"}
                tr[key + ".desc"] = desc_tr or desc_en
    en_path.write_text(json.dumps(en, indent=2, ensure_ascii=False) + "\n")
    tr_path.write_text(json.dumps(dict(sorted(tr.items())), indent=2, ensure_ascii=False) + "\n")

    # Pages.
    for name, page in PARAGRAPH_PAGES.items():
        heading_key, prefix, _ = SECTIONS[name]
        section = data[name]
        body = heading_html(heading_key, section["heading"]["en"])
        body += "".join("\n" + item_html(prefix + i["id"], i, block=True) + "\n" for i in section["items"])
        replace_letter_body(SITE / page, body)

    body = heading_html(SECTIONS["values"][0], data["values"]["heading"]["en"]) + "\n"
    body += section_list(data, "values") + "\n"
    body += heading_html(SECTIONS["principles"][0], data["principles"]["heading"]["en"], spaced=True) + "\n"
    body += section_list(data, "principles")
    replace_letter_body(SITE / "values/index.html", body)


if __name__ == "__main__":
    build()
    print("Built Mission, Values, Projects, Writing and Join Us from site-text.json")
