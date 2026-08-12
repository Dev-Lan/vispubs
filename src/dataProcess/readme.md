# Data processing and release procedure

This directory holds the data ingestion pipeline for [vispubs.com](https://vispubs.com). It covers
IEEE VIS (and its historical InfoVis / VAST / SciVis tracks), EuroVis, and CHI.

Everything below assumes you are running from this directory:

```bash
cd src/dataProcess
```

All scripts use relative paths (`./input/`, `./temp/`, `../../public/data/`), so running them from
anywhere else will fail or write to the wrong place.

A full release has five phases:

1. [Manual preparation](#1-manual-preparation) — gather inputs the pipeline cannot fetch itself
2. [Run the pipeline](#2-run-the-pipeline) — `python main.py`
3. [Review](#3-review) — validation report, changelog, log
4. [Deploy the site](#4-deploy-the-site)
5. [Publish the Hugging Face dataset release](#5-publish-the-hugging-face-dataset-release)
6. [Announce](#6-announce)

---

## 1. Manual preparation

### dblp snapshot (required)

The pipeline reads a full dblp dump. Download a current one — a stale snapshot silently yields zero
new papers for recent venues rather than an error:

```bash
curl -o ./input/dblp.dtd https://dblp.org/xml/dblp.dtd
curl -o ./input/dblp.xml.gz https://dblp.org/xml/dblp.xml.gz
gunzip ./input/dblp.xml.gz
```

The uncompressed file is roughly 5 GB. `./input/` is gitignored, so nothing here is committed.
Consider keeping the previous snapshot under a dated name (e.g. `dblp-2025-10-31.xml`) for
reproducibility.

### Awards (required if the cycle had awards)

Award data is not in dblp and must be entered by hand.

- **VIS and EuroVis** → `./input/awards.csv`, columns `Title,Award`. This is a **per-cycle scratch
  file**, not an accumulating record: awards from previous cycles are already baked into the
  intermediate CSVs, so replacing its contents each cycle is expected.
- **CHI** → `./input/chi_awards.csv`, a historical record spanning multiple years. **Append** to
  this one. It is _not_ wired into `main.py`; CHI awards were historically applied by
  `archive/merge_chi_awards.py` from CHI program JSON files.

Award codes: `BP` (Best Paper), `HM` (Honorable Mention), `BCS` (Best Case Study),
`BA` (Best Application), `TT` (Test of Time).

Sources: [ieeevis.org](https://ieeevis.org/) for VIS,
[EG digital library](https://diglib.eg.org/) for EuroVis, the CHI program for CHI.

Awards must be in place **before** running the pipeline. `main.py` applies them to an intermediate
temp file partway through the run, so awards added afterwards are silently ignored.

`awards.py` matches on exact title. dblp strips trailing periods from titles and may differ in
punctuation or capitalization from the award announcement, so expect to hand-align a title or two.
Any award row that fails to match is logged as `ERROR: Rows in the award file not found in the
paper file` — check for that in the log rather than assuming the merge worked.

### Author deduplication

Author names come from dblp already disambiguated (e.g. `Bei Wang 0001`), which is why dblp is the
source of truth for names. Ambiguous cases that dblp has not resolved still need manual review.
`archive/dedup-authors.py` and `archive/merge_authors.py` are the historical tooling for this.

### Early access papers (VIS only, optional)

VIS papers can be loaded before they appear in TVCG, using the conference program data. This is a
separate manual flow, not part of `main.py`:

- `ingest_vis_25.py` (and `ingest_vis_24.py`) build rows from `./input/vis25/` program exports,
  assigning placeholder DOIs of the form `EARLY_ACCESS/<id>` and setting `Early` to true.
- Once the papers are published for real, `update_doi.py` replaces the placeholder DOIs with the
  actual ones and refreshes abstracts.

Author names from this path come from the conference program, **not** dblp, so they are not
deduplicated and need correcting against dblp once the papers are indexed.

### IEEE Xplore export (for resolving early-access DOIs)

dblp is the source of truth for regular ingestion, but real DOIs for early-access papers come from
IEEE Xplore before dblp indexes them. `update_doi.py` reads this export from
`./temp/vis25_from_ieee_jan.csv`.

To produce it:

1. Wait until January, when the VIS papers appear in the TVCG issue. (Doing this earlier means
   cross-checking early-access papers against a published list by hand.)
2. Go to the January TVCG issue on [ieeexplore.ieee.org](https://ieeexplore.ieee.org/).
3. Select all, then manually deselect anything that is not a paper (front cover, editorials, and so
   on).
4. Export as BibTeX, with **citation and abstract** included. Set items per page to 100 to keep this
   to a few pages; multiple exports may be needed.
5. Convert to CSV. `archive/bib_to_csv.py` is the historical tool for this and requires editing
   filenames inside the script.

Since the columns `update_doi.py` expects are `Conference,Year,Title,DOI,Abstract,...`, matching is
by title — see the script's docstring for details.

---

## 2. Run the pipeline

```bash
python main.py
```

This runs the whole ingestion as one sequence — do not run the individual scripts by hand unless
you are debugging a specific step. In order, it:

| #   | Step                       | What it does                                                              |
| --- | -------------------------- | ------------------------------------------------------------------------- |
| 1   | `parse_large_xml_with_dtd` | Coarsely filters the ~5 GB dblp dump to `./temp/dblp_filtered.xml`        |
| 2   | `dblp_to_csv`              | Converts to CSV and classifies venues → `./temp/potential_new_papers.csv` |
| 3   | `filter_to_new`            | Diffs against the intermediate files, keeping only genuinely new papers   |
| 4   | `add_awards`               | Merges `./input/awards.csv` by title                                      |
| 5   | `add_abstracts`            | Fetches abstracts from Semantic Scholar, falling back to Crossref         |
| 6   | `update_intermediate`      | Appends new papers to `./intermediate/{VIS,eurovis,chi}.csv`              |
| 7   | `filter_to_vis_papers`     | Filters CHI to visualization-relevant papers by keyword                   |
| 8   | `combine`                  | Merges the intermediates into `../../public/data/papers.csv`              |
| 9   | `create_stub_files`        | Creates resource-link stub files for new papers                           |
| 10  | `search_preprint_versions` | Looks for preprint versions                                               |
| 11  | `update_paper_link_flags`  | Recomputes the `Resources` column                                         |
| 12  | `generate_parquet`         | Writes `papers.parquet` and `authors.parquet`                             |
| 13  | `update_changelog`         | Prepends a dated entry to `../../public/data/changelog.md`                |
| 14  | `validate_data`            | Writes `./report.md`                                                      |

### Venue classification

Venue detection lives in `parse_dblp_xml.py`. It is heuristic and **fails silently** — if a venue
changes how it publishes, you get zero papers rather than an error. Verify counts after every run.

- **CHI** — `booktitle == 'CHI'`
- **VIS** — `IEEE Trans. Vis. Comput. Graph.`, issue 1 (issue 2 for 2021), year > 2016. The `Year`
  column is set to the dblp year **minus one**, because the TVCG issue appears the January after the
  conference. This offset applies to VIS only.
- **EuroVis** — `Comput. Graph. Forum`, issue 3, year > 2007

### Expect a long run

`add_abstracts` sleeps 2 seconds per paper and runs _before_ the CHI keyword filter, so abstracts
are fetched for every new CHI paper even though only about 7% survive filtering. CHI alone has run
600–1,250 papers per year, so budget 45+ minutes for that step. The run is not hung.

---

## 3. Review

Nothing here is automatic — inspect all three before deploying.

- **`./report.md`** — validation report from `validate_data.py`. Checks for empty abstracts
  (error), duplicate DOIs (error), and duplicate titles (warning). Duplicate titles across
  different venues are often legitimate; duplicate DOIs never are.
- **`../../public/data/changelog.md`** — confirm the new dated entry has sensible per-conference
  counts and year ranges.
- **`./temp/data_ingestion.log`** — full DEBUG log of the run. Check here for award rows that
  failed to match and abstracts that failed to fetch.

Also sanity-check the new paper counts per venue against previous years, and skim for front matter
or non-paper entries that slipped past `is_front_matter` (editorials, keynotes, capstones).

---

## 4. Deploy the site

```bash
quasar dev                  # test locally
quasar build                # production build
npx http-server dist/spa    # test the build
```

Then publish, and verify [www.vispubs.com](https://www.vispubs.com) once it is live. There are two
ways to publish:

- **GitHub Action** (`.github/workflows/deploy.yaml`) — `workflow_dispatch` only, so it must be
  triggered manually from the Actions tab or with `gh workflow run deploy.yaml`. It does its own
  `quasar build`, so the local build above is a check rather than the artifact that ships.
- **Locally** — `yarn deploy`, which pushes `dist/spa` to the `gh-pages` branch via `push-dir`.

Note that merging a data change to `main` also triggers `.github/workflows/generate-sitemap.yaml`
automatically, because it watches `public/data/papers.csv`. That workflow regenerates
`public/sitemap.xml` and commits it back to `main` on its own — so expect an extra
`chore: regenerate sitemap.xml` commit to appear without your involvement.

---

## 5. Publish the Hugging Face dataset release

The dataset lives at
[huggingface.co/datasets/DevLan/vispubs](https://huggingface.co/datasets/DevLan/vispubs). Only
`papers.parquet` is published — `authors.parquet` is not.

Publish **after** `generate_parquet` has run and the validation report is clean. The upload takes
whatever is currently in `public/data/papers.parquet`, so a release made before the review phase
ships unreviewed data.

### Prerequisites

```bash
pip install huggingface_hub
huggingface-cli login       # or set the HF_TOKEN environment variable
```

### Publish a release

```bash
python upload_hf_dataset.py --version v2026.1 --message "Add EuroVis 2026 and CHI 2026 papers"
```

Both flags are required. This uploads the parquet file, regenerates the dataset card, appends a
changelog entry to it, and creates a git tag on the HF repo.

### Update only the dataset card

```bash
python upload_hf_dataset.py --readme-only
```

No data upload, no version tag. Use this to fix schema documentation or wording between releases.

### Versioning policy

Versions are `v{year}.{minor}` with an optional `-{prerelease}` suffix.

- **`{year}`** is the data cycle the release belongs to — `v2026.x` for the 2026 ingest season.
- **`{minor}`** increments on **every** publish, regardless of how small the change is. There is no
  judgment call about whether a change is "big enough" to tag.
- When the cycle rolls over to a new year, `{minor}` resets to `0` — so `v2026.4` is followed by
  `v2027.0`.

Prerelease suffixes:

| Suffix   | Meaning                                    |
| -------- | ------------------------------------------ |
| `-alpha` | Early testing; the schema may still change |
| `-beta`  | Near-stable; minor adjustments possible    |
| _(none)_ | Stable release                             |

**Current state:** the dataset is in `-alpha` while the schema may still change.

The format is enforced by a regex in `upload_hf_dataset.py`, which rejects anything that does not
match (`v2026.0`, `v2026.1-alpha`, and `v2026.2-beta` are all valid).

### How consumers pin a version

Every release creates a tag on the HF repo, so a specific version can be loaded by revision:

```python
from datasets import load_dataset

ds = load_dataset("DevLan/vispubs")                              # latest
ds = load_dataset("DevLan/vispubs", revision="v2026.0-alpha")    # pinned
```

This is the reason to tag every publish rather than only significant ones: an untagged upload is
not addressable, so anyone pinning to a version gets data that silently differs from what was
published.

### Editing the dataset card

The card body is regenerated from `DATASET_CARD_TEMPLATE` in `upload_hf_dataset.py` on **every**
run. Edit that template — anything typed into the Hugging Face web editor is overwritten on the
next publish. Changelog entries are the exception: they are read back off the remote card and
preserved.

---

## 6. Announce

Post to Twitter/X, Mastodon, Bluesky, and LinkedIn.

---

## Other update flows

Not every change is a full ingest.

- **An author submits a homepage** — update `../../public/data/authors.csv`, add a changelog entry,
  regenerate parquet, deploy.
- **An author submits resource links** — update the relevant file in
  `../../public/data/paperLinks/`, run `update_paper_link_flags.py`, add a changelog entry,
  regenerate parquet, deploy.

Both of these change `papers.parquet`, so they warrant an HF release under the same versioning
policy.
