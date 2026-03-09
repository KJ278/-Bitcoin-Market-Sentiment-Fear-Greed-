import { normalizeEvents } from "../utils/normalizeEvents.js";

/**
 * BookMyShow scraper module.
 * In production, replace SAMPLE_EVENTS with real parsing/API logic.
 */
const SAMPLE_EVENTS = [
  {
    title: "BookMyShow Indie Music Fest",
    date: new Date(Date.now() + 86400000).toISOString(),
    location: "Mumbai",
    price: "₹499 onwards",
    url: "https://in.bookmyshow.com/explore/events-mumbai",
    image: "https://placehold.co/640x360?text=BookMyShow"
  },
  {
    title: "BookMyShow Standup Spotlight",
    date: new Date(Date.now() + 172800000).toISOString(),
    location: "Pune",
    price: "₹799",
    url: "https://in.bookmyshow.com/explore/comedy-shows-mumbai",
    image: "https://placehold.co/640x360?text=Comedy"
  }
];

export async function fetchBookMyShowEvents() {
  try {
    // Placeholder fetch to show graceful handling pattern for remote sources.
    await fetch("https://in.bookmyshow.com/", { method: "GET", mode: "no-cors" });
    return normalizeEvents(SAMPLE_EVENTS, "BookMyShow");
  } catch (error) {
    console.warn("[EventHub] BookMyShow fetch failed; using fallback data.", error);
    return normalizeEvents(SAMPLE_EVENTS, "BookMyShow");
  }
}
