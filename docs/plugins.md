# VisPubs plugin framework

VisPubs supports third-party plugins that render alongside the paper list. A plugin is just a URL that serves HTML/JS — a GitHub gist raw URL, a CodePen export, a self-hosted page, or a file in this repo's `public/plugins/` folder.

Plugins are activated per-session via a query parameter, so any plugin link is shareable.

## Loading a plugin

```
https://vispubs.com/?plugin=<url>
https://vispubs.com/?plugin=<url>&pluginOrientation=vertical
```

- `plugin` — the plugin URL. Relative URLs resolve against vispubs's origin.
- `pluginOrientation` — `horizontal` (default, side-by-side) or `vertical` (stacked).

On first load of a new plugin URL, vispubs shows a confirmation dialog naming the origin. Approval is session-scoped: reloading the tab re-prompts, and sharing a link always re-prompts in the recipient's session.

Reference plugin: [`/plugins/example-scatterplot.html`](../public/plugins/example-scatterplot.html).

```
https://vispubs.com/?plugin=/plugins/example-scatterplot.html
```

## Security model

Plugins load inside `<iframe sandbox="allow-scripts">`. No `allow-same-origin`, no forms, no storage, no popups. This means a plugin:

- Cannot read cookies, localStorage, sessionStorage, or IndexedDB on vispubs.com.
- Cannot touch the parent DOM or any other origin's data.
- Cannot navigate the top window or open popups.
- Receives data only through `postMessage` from the host.

All data the host sends (from `papers.csv`) is already public, so the sandbox is defense-in-depth: it protects users against a malicious shared `?plugin=...` link, not against exposure of sensitive data.

## Message protocol

All messages use a `vispubs:` type prefix. Anything without that prefix is ignored. Plugins should send messages to `window.parent` with target origin `'*'`.

### Host → plugin

The host sends `vispubs:state` in response to `vispubs:ready`, then again on every relevant reactive change (debounced ~150 ms).

```ts
{
  type: 'vispubs:state',
  papers: PluginPaper[],         // current filtered list, in display order
  filters: PluginFilterState,    // search, year, venue, award, resource, collection
  selectedDoi: string | null,    // paper open in the detail drawer
  focusedDoi: string | null,     // paper highlighted (keyboard/hover focus)
  darkMode: boolean,
}
```

See [`src/types/plugin.ts`](../src/types/plugin.ts) for the full shape, including `PluginPaper` and `PluginFilterState`.

### Plugin → host

| Message | Effect |
| --- | --- |
| `{ type: 'vispubs:ready' }` | Tells the host the plugin is wired and requests the initial state. Send this once after your message listener is attached. |
| `{ type: 'vispubs:selectPaper', doi }` | Opens the paper with the given DOI in the right-side detail drawer. |
| `{ type: 'vispubs:focusPaper', doi }` | Highlights the paper in the list. Pass `doi: null` to clear focus. |

The host validates every incoming message:

- `event.source` must match the plugin's iframe window. Messages from other frames are ignored.
- Messages whose `type` is missing or doesn't start with `vispubs:` are dropped.
- `selectPaper`/`focusPaper` are no-ops if the DOI is not in the current filtered list.

## Minimal plugin template

```html
<!doctype html>
<html>
  <body>
    <pre id="out"></pre>
    <script>
      window.addEventListener('message', (event) => {
        if (!event.data || event.data.type !== 'vispubs:state') return;
        document.getElementById('out').textContent =
          event.data.papers.length + ' papers';
      });
      window.parent.postMessage({ type: 'vispubs:ready' }, '*');
    </script>
  </body>
</html>
```

## Out of scope

- Multiple plugins at once.
- In-repo Vue-component plugins (same protocol, no iframe) — may land later.
- Plugin contributions to FilterPanel, PaperInformation, or new top-level routes.
- A persistent plugin registry or curated plugin picker in the UI.
- Plugin-provided filter dimensions that feed back into the host's paper set.
