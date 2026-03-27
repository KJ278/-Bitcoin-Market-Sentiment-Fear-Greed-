import { fetchBookMyShowEvents } from "./scrapers/bookmyshow.js";
import { fetchInsiderEvents } from "./scrapers/insider.js";
import { fetchDistrictEvents } from "./scrapers/district.js";

const ALARM_NAME = "eventhub-refresh";
const REFRESH_MINUTES = 360; // 6 hours
const MAX_EVENTS = 50;

async function aggregateAllEvents() {
  const [bookmyshow, insider, district] = await Promise.all([
    fetchBookMyShowEvents(),
    fetchInsiderEvents(),
    fetchDistrictEvents()
  ]);

  return [...bookmyshow, ...insider, ...district]
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .slice(0, MAX_EVENTS);
}

async function refreshAndCacheEvents() {
  try {
    const events = await aggregateAllEvents();
    await chrome.storage.local.set({
      events,
      lastUpdated: new Date().toISOString(),
      lastError: null
    });
  } catch (error) {
    await chrome.storage.local.set({
      lastError: error?.message || "Failed to refresh events"
    });
  }
}

chrome.runtime.onInstalled.addListener(async () => {
  await chrome.alarms.create(ALARM_NAME, { periodInMinutes: REFRESH_MINUTES });
  await refreshAndCacheEvents();
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === ALARM_NAME) {
    await refreshAndCacheEvents();
  }
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type === "EVENTHUB_REFRESH") {
    refreshAndCacheEvents()
      .then(() => sendResponse({ ok: true }))
      .catch((error) => sendResponse({ ok: false, error: error?.message || "Unknown error" }));
    return true;
  }

  return false;
});
