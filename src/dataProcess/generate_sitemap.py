"""Generate an XML sitemap for VisPubs from papers.csv."""

import csv
import os
from datetime import date
from urllib.parse import quote

BASE_URL = "https://vispubs.com"
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PAPERS_CSV = os.path.join(REPO_ROOT, "public", "data", "papers.csv")
SITEMAP_OUT = os.path.join(REPO_ROOT, "public", "sitemap.xml")


def read_dois(csv_path):
    dois = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doi = row["DOI"].strip()
            if doi:
                dois.append(doi)
    return dois


def generate_sitemap(dois):
    today = date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url>",
        f"    <loc>{BASE_URL}/</loc>",
        f"    <lastmod>{today}</lastmod>",
        "    <priority>1.0</priority>",
        "  </url>",
        "  <url>",
        f"    <loc>{BASE_URL}/about</loc>",
        f"    <lastmod>{today}</lastmod>",
        "    <priority>0.8</priority>",
        "  </url>",
    ]
    for doi in dois:
        encoded_doi = quote(doi, safe="")
        lines.append("  <url>")
        lines.append(f"    <loc>{BASE_URL}/?paper={encoded_doi}</loc>")
        lines.append("    <priority>0.5</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    dois = read_dois(PAPERS_CSV)
    xml = generate_sitemap(dois)
    with open(SITEMAP_OUT, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Generated sitemap with {len(dois) + 2} URLs ({len(dois)} papers + 2 static pages)")
    print(f"Written to {os.path.abspath(SITEMAP_OUT)}")


if __name__ == "__main__":
    main()
