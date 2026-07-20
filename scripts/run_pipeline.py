"""Orchestration pipeline for lead generation"""
import os
import argparse
from src.extractors.search_api import search_businesses
from src.enrich.scraper import extract_contacts_from_website
from src.storage.sheets_client import StorageClient
from src.ai.email_generator import generate_email
from src.outreach.simulator import simulate_outreach


def run_pipeline(category: str, city: str, num: int = 10):
    serpapi_key = os.environ.get("SERPAPI_API_KEY")
    print(f"Searching for '{category}' in '{city}' (max {num})")
    results = search_businesses(category, city, serpapi_key=serpapi_key, num=num)
    print(f"Found {len(results)} results from search API")
    storage = StorageClient()
    for idx, r in enumerate(results, start=1):
        name = r.get("name")
        website = r.get("website")
        print(f"[{idx}/{len(results)}] Processing: {name} - {website}")
        contacts = {"email": None, "phone": None}
        if website:
            try:
                c = extract_contacts_from_website(website)
                contacts.update({k: v for k, v in c.items() if k in ("email", "phone")})
            except Exception as e:
                print(f"  - Error scraping site: {e}")
        entry = {
            "name": name,
            "website": website or "",
            "phone": r.get("phone") or contacts.get("phone") or "",
            "email": contacts.get("email") or r.get("phone") or "",
            "address": r.get("address") or "",
            "rating": r.get("rating") or "",
        }
        # Generate email using AI
        email_data = generate_email(entry)
        entry.update({"email_subject": email_data.get("subject"), "email_body": email_data.get("body"), "note": email_data.get("note")})
        # Simulate outreach
        outreach_res = simulate_outreach(entry)
        entry.update({"outreach_status": outreach_res.get("status"), "outreach_message": outreach_res.get("message")})
        # Save
        try:
            storage.append_row(entry)
            print(f"  - Saved lead: status={entry['outreach_status']}")
        except Exception as e:
            print(f"  - Error saving lead: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", required=True)
    parser.add_argument("--city", required=True)
    parser.add_argument("--num", type=int, default=10)
    args = parser.parse_args()
    run_pipeline(args.category, args.city, args.num)
