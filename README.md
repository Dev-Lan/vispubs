# Visualization Publications (VisPubs)

This repo contains the code and data for the [vispubs.com](https://vispubs.com) website. The goal of this project is to create a nice interface for finding relevant visualization publications across multiple venues.

## Dataset on Hugging Face

The paper metadata is published as a dataset at [DevLan/vispubs](https://huggingface.co/datasets/DevLan/vispubs), which is the easiest way to work with it in Python.

```bash
pip install datasets
```

```python
from datasets import load_dataset

ds = load_dataset("DevLan/vispubs")
print(ds["train"].to_pandas().head())
```

Every publish is tagged, so a specific release can be pinned — useful when you want an analysis to stay reproducible as the data grows:

```python
ds = load_dataset("DevLan/vispubs", revision="v2026.6")
```

Versions are `v{year}.{minor}`: the year tracks the ingest cycle and the minor number increments on every publish. The tag list on the dataset page shows what is available.

A few things worth knowing:

- It contains `papers.parquet` only. The author-homepage table is not published there.
- The Parquet stores `AuthorNames-Deduped`, `Award`, and `Resources` as **list** columns, and adds a `ResourceLinks` struct column that the CSV export does not have — so it is a superset of the CSV, not a copy of it.
- The site's export dialog will generate a snippet that reproduces whatever filters you have applied, so you do not have to translate them by hand.

## Licenses

In spirit this is an open-source academic project. If the data, analysis code, or front-end code are useful in some way, then use them. If you do use them (especially in an academic publication), then please cite this work. See the [about page](https://vispubs.com/about) for best way to cite this work.

For the specific Licenses I use two different licenses. One for the data files, and one for the analysis/front-end code.

- Data Files (everything in public/data): CC-By 4.0, International. See LICENSE-DATA.md.
- Other Code (everything else): Apache 2.0. See LICENSE.

# For Developer

## Install the dependencies

```bash
yarn
# or
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)

```bash
quasar dev
```

### Lint the files

```bash
yarn lint
# or
npm run lint
```

### Format the files

```bash
yarn format
# or
npm run format
```

### Build the app for production

```bash
quasar build
```

### Deploy to github pages production

```bash
yarn deploy
```

### Customize the configuration

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js).
