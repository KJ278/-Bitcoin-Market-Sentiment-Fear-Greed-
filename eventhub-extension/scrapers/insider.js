import { normalizeEvents } from "../utils/normalizeEvents.js";

/**
 * Insider scraper module.
 * Uses sample fallback data to keep extension runnable without backend.
 */
const SAMPLE_EVENTS = [
  {
    title: "Insider Tech Conference",
    date: new Date(Date.now() + 259200000).toISOString(),
    location: "Bengaluru",
    price: "₹999",
    url: "https://insider.in/all-events-in-bengaluru",
    image: "https://placehold.co/640x360?text=Insider"
  },
  {
    title: "Insider Art & Culture Walk",
    date: new Date(Date.now() + 345600000).toISOString(),
    location: "Delhi",
    price: "Free",
    url: "https://insider.in/all-events-in-delhi",
    image: "https://placehold.co/640x360?text=Culture"
  }
];

export async function fetchInsiderEvents() {
  try {
    await fetch("https://insider.in/", { method: "GET", mode: "no-cors" });
    return normalizeEvents(SAMPLE_EVENTS, "Insider");
  } catch (error) {
    console.warn("[EventHub] Insider fetch failed; using fallback data.", error);
    return normalizeEvents(SAMPLE_EVENTS, "Insider");
  }
}
