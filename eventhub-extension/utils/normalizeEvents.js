/**
 * Normalize one event object into EventHub's canonical shape.
 */
export function normalizeEvent(rawEvent = {}, platform = "Unknown") {
  return {
    title: rawEvent.title || rawEvent.name || "Untitled Event",
    platform,
    date: rawEvent.date || rawEvent.startDate || "TBA",
    location: rawEvent.location || rawEvent.city || "Unknown",
    price: rawEvent.price || rawEvent.priceDisplay || "N/A",
    url: rawEvent.url || rawEvent.link || "#",
    image: rawEvent.image || rawEvent.poster || "https://placehold.co/640x360?text=EventHub"
  };
}

/**
 * Normalize a list and remove obvious duplicates.
 */
export function normalizeEvents(rawEvents = [], platform = "Unknown") {
  const seen = new Set();

  return rawEvents
    .map((event) => normalizeEvent(event, platform))
    .filter((event) => {
      const dedupeKey = `${event.platform}|${event.title}|${event.date}|${event.location}`;
      if (seen.has(dedupeKey)) return false;
      seen.add(dedupeKey);
      return true;
    });
}
