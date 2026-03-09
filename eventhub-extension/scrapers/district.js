import { normalizeEvents } from "../utils/normalizeEvents.js";

/**
 * District scraper module.
 * Uses sample fallback data to keep extension stable in local demos.
 */
const SAMPLE_EVENTS = [
  {
    title: "District Food Carnival",
    date: new Date(Date.now() + 432000000).toISOString(),
    location: "Hyderabad",
    price: "₹299 onwards",
    url: "https://district.in/",
    image: "https://placehold.co/640x360?text=District"
  },
  {
    title: "District Startup Mixer",
    date: new Date(Date.now() + 518400000).toISOString(),
    location: "Chennai",
    price: "₹199",
    url: "https://district.in/",
    image: "https://placehold.co/640x360?text=Startup"
  }
];

export async function fetchDistrictEvents() {
  try {
    await fetch("https://district.in/", { method: "GET", mode: "no-cors" });
    return normalizeEvents(SAMPLE_EVENTS, "District");
  } catch (error) {
    console.warn("[EventHub] District fetch failed; using fallback data.", error);
    return normalizeEvents(SAMPLE_EVENTS, "District");
  }
}
