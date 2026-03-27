# EventHub Chrome Extension (Manifest V3)

EventHub is a Chrome extension that aggregates events from BookMyShow, Insider, and District in one unified popup dashboard.

## Folder structure

```text
eventhub-extension/
  manifest.json
  background.js
  popup.html
  popup.css
  popup.js
  scrapers/
    bookmyshow.js
    insider.js
    district.js
  utils/
    normalizeEvents.js
  README.md
```

## Features

- Manifest V3 extension with background service worker.
- Aggregates events from multiple platforms into one list.
- Stores cached events in `chrome.storage.local`.
- Auto-refresh every 6 hours using `chrome.alarms`.
- Manual refresh button in popup.
- Filters by platform and date.
- Displays up to 50 events.
- Graceful error handling with fallback sample data.

## About icons (important)

This repository intentionally **does not include binary icon files**.

If you want toolbar/extension icons:
1. Create `icon16.png`, `icon48.png`, and `icon128.png`.
2. Put them in `eventhub-extension/icons/`.
3. Add an `icons` block in `manifest.json`:

```json
"icons": {
  "16": "icons/icon16.png",
  "48": "icons/icon48.png",
  "128": "icons/icon128.png"
}
```

## Load unpacked in Chrome

1. Open Chrome and go to `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select the `eventhub-extension/` folder.
5. Click the EventHub icon to open the popup dashboard.

## Notes for production

- The current scrapers include sample fallback data to keep the extension runnable.
- Replace sample arrays in `scrapers/*.js` with real endpoint parsing/API integrations.
- Keep normalization via `utils/normalizeEvents.js` so UI logic stays consistent.
