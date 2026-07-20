"""SerpAPI-based business search wrapper"""
import os
import requests

SERPAPI_URL = "https://serpapi.com/search.json"

def search_businesses(category: str, city: str, serpapi_key: str = None, num: int = 10):
    """Return a list of dicts with: name, website, phone, rating, address, serpapi_result"""
    if serpapi_key is None:
        serpapi_key = os.environ.get("SERPAPI_API_KEY")
    params = {
        "engine": "google_maps",
        "type": "search",
        "q": f"{category} in {city}",
        "hl": "en",
        "num": num,
        "api_key": serpapi_key,
    }
    resp = requests.get(SERPAPI_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for place in data.get("local_results", {}).get("places", []) or data.get("local_results", {}).get("organic_results", []):
        entry = {
            "name": place.get("title") or place.get("name"),
            "address": place.get("address"),
            "rating": place.get("rating"),
            "website": place.get("website"),
            "phone": place.get("phone"),
            "serpapi_result": place,
        }
        results.append(entry)
    # Fallback: some SerpAPI responses include 'map_results' or 'local_results' variants
    if not results and "map_results" in data:
        for place in data.get("map_results", {}).get("places", []):
            results.append({
                "name": place.get("title"),
                "address": place.get("address"),
                "rating": place.get("rating"),
                "website": place.get("website"),
                "phone": place.get("phone"),
                "serpapi_result": place,
            })
    return results[:num]
