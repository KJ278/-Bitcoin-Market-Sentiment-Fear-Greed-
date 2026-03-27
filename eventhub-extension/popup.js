const refreshBtn = document.getElementById("refreshBtn");
const platformFilter = document.getElementById("platformFilter");
const dateFilter = document.getElementById("dateFilter");
const statusText = document.getElementById("statusText");
const eventsContainer = document.getElementById("eventsContainer");

let cachedEvents = [];

function formatDate(dateString) {
  const parsed = new Date(dateString);
  if (Number.isNaN(parsed.getTime())) return dateString;
  return parsed.toLocaleString();
}

function render(events) {
  eventsContainer.innerHTML = "";

  if (!events.length) {
    statusText.textContent = "No events found for selected filters.";
    return;
  }

  statusText.textContent = `Showing ${events.length} event(s)`;

  for (const event of events) {
    const card = document.createElement("article");
    card.className = "card";

    card.innerHTML = `
      <img src="${event.image}" alt="${event.title}" loading="lazy" />
      <div class="card-content">
        <span class="badge">${event.platform}</span>
        <h2>${event.title}</h2>
        <p class="meta">📅 ${formatDate(event.date)}</p>
        <p class="meta">📍 ${event.location}</p>
        <p class="meta">💸 ${event.price}</p>
        <a class="view-link" href="${event.url}" target="_blank" rel="noreferrer">View Event</a>
      </div>
    `;

    eventsContainer.appendChild(card);
  }
}

function applyFilters() {
  const platformValue = platformFilter.value;
  const dateValue = dateFilter.value;

  const filtered = cachedEvents.filter((event) => {
    const platformMatch = platformValue === "all" || event.platform === platformValue;
    const dateMatch = !dateValue || String(event.date).startsWith(dateValue);
    return platformMatch && dateMatch;
  });

  render(filtered);
}

async function loadFromStorage() {
  const data = await chrome.storage.local.get(["events", "lastUpdated", "lastError"]);
  cachedEvents = (data.events || []).slice(0, 50);

  applyFilters();

  if (data.lastError) {
    statusText.textContent = `Warning: ${data.lastError}`;
  } else if (data.lastUpdated) {
    statusText.textContent += ` • Updated ${new Date(data.lastUpdated).toLocaleString()}`;
  }
}

async function manualRefresh() {
  statusText.textContent = "Refreshing events...";

  try {
    const response = await chrome.runtime.sendMessage({ type: "EVENTHUB_REFRESH" });
    if (!response?.ok) {
      statusText.textContent = `Refresh failed: ${response?.error || "Unknown error"}`;
      return;
    }
    await loadFromStorage();
  } catch (error) {
    statusText.textContent = `Refresh failed: ${error?.message || "Unknown error"}`;
  }
}

refreshBtn.addEventListener("click", manualRefresh);
platformFilter.addEventListener("change", applyFilters);
dateFilter.addEventListener("change", applyFilters);

document.addEventListener("DOMContentLoaded", loadFromStorage);
