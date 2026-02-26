"""Ingest video links from IEEE VIS program data into paperLinks files.

Fetches the program papers.json from the ieee-vgtc/ieeevis.org GitHub repo
for a given year and adds video links (presentation, fast-forward, session
recordings) to the corresponding paperLinks CSV files.

Matching is done by paper title (case-insensitive) against papers.csv, since
DOIs in the program JSON often differ from the final published DOIs in
papers.csv.

Usage:
    python ingest_vis_videos.py --year 2024
    python ingest_vis_videos.py --year 2025

Source data:
    https://raw.githubusercontent.com/ieee-vgtc/ieeevis.org/vis{year}/program/papers.json

Video fields by year:
    2024: prerecorded_video_link, youtube_ff_url, session_bunny_ff_link
    2025: youtube_url, youtube_ff_url, session_youtube_url, session_bunny_ff_link
"""

import argparse
import csv
import json
import os
import re
import urllib.request

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
PAPERS_CSV = os.path.join(REPO_ROOT, "public", "data", "papers.csv")
PAPER_LINKS_DIR = os.path.join(REPO_ROOT, "public", "data", "paperLinks")
SOURCE_URL = "https://raw.githubusercontent.com/ieee-vgtc/ieeevis.org/vis{year}/program/papers.json"


def build_title_to_doi_map():
    """Build a case-insensitive title -> DOI lookup from papers.csv."""
    title_map = {}
    with open(PAPERS_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = (row.get("Title") or "").strip().lower()
            doi = (row.get("DOI") or "").strip()
            if title and doi:
                title_map[title] = doi
    return title_map


def normalize_youtube_url(url):
    """Convert embed/nocookie YouTube URLs to standard youtu.be format."""
    if not url:
        return url
    match = re.match(r"https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([^?&/]+)", url)
    if match:
        video_id = match.group(1)
        return f"https://youtu.be/{video_id}"
    return url


def read_existing_urls(filepath):
    """Read existing URLs from a paperLinks CSV file."""
    if not os.path.isfile(filepath):
        return set()
    urls = set()
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("url") or "").strip()
            if url:
                urls.add(url)
    return urls


def append_links(filepath, links):
    """Append new video links to a paperLinks CSV file."""
    if not os.path.isfile(filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write("name,url,icon\n")

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for name, url, icon in links:
            writer.writerow([name, url, icon])


def extract_video_links(entry):
    """Extract video links from a program JSON entry."""
    links = []

    # Presentation video
    for field in ["youtube_url", "prerecorded_video_link"]:
        url = (entry.get(field) or "").strip()
        if url:
            links.append(("Presentation", normalize_youtube_url(url), "video"))
            break

    # Fast-forward video
    url = (entry.get("youtube_ff_url") or "").strip()
    if url:
        links.append(("Fast Forward", normalize_youtube_url(url), "video"))

    # Session recording
    for field in ["session_youtube_url", "session_bunny_ff_link"]:
        url = (entry.get(field) or "").strip()
        if url:
            links.append(("Session Recording", normalize_youtube_url(url), "video"))
            break

    return links


def main():
    parser = argparse.ArgumentParser(description="Ingest VIS video links into paperLinks")
    parser.add_argument("--year", required=True, type=int, help="VIS conference year (e.g., 2024)")
    args = parser.parse_args()

    url = SOURCE_URL.format(year=args.year)
    print(f"Fetching {url}...")

    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))

    print(f"Found {len(data)} entries in program JSON")
    print("Building title lookup from papers.csv...")
    title_to_doi = build_title_to_doi_map()

    stats = {
        "matched": 0,
        "videos_added": 0,
        "skipped_no_video": 0,
        "skipped_no_match": 0,
        "skipped_duplicate": 0,
    }

    for entry in data:
        title = (entry.get("title") or "").strip().lower()
        if not title:
            stats["skipped_no_match"] += 1
            continue

        doi = title_to_doi.get(title)
        if not doi:
            stats["skipped_no_match"] += 1
            continue

        video_links = extract_video_links(entry)
        if not video_links:
            stats["matched"] += 1
            stats["skipped_no_video"] += 1
            continue

        stats["matched"] += 1
        filepath = os.path.join(PAPER_LINKS_DIR, doi)
        existing_urls = read_existing_urls(filepath)
        new_links = []
        for name, link_url, icon in video_links:
            if link_url not in existing_urls:
                new_links.append((name, link_url, icon))
            else:
                stats["skipped_duplicate"] += 1

        if new_links:
            append_links(filepath, new_links)
            stats["videos_added"] += len(new_links)

    print(f"\n--- Summary for VIS {args.year} ---")
    print(f"Papers matched by title: {stats['matched']}")
    print(f"Videos added: {stats['videos_added']}")
    print(f"Skipped (no title match in papers.csv): {stats['skipped_no_match']}")
    print(f"Skipped (matched but no video URLs): {stats['skipped_no_video']}")
    print(f"Skipped (duplicate URL already in file): {stats['skipped_duplicate']}")


if __name__ == "__main__":
    main()
