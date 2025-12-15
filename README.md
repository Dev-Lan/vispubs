# Visualization Publications (vispubs)

This repo contains the code and data for the [vispubs.com](https://vispubs.com) website. The goal of this project is to create a nice interface for finding relevant visualization publications across multiple venues.

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
