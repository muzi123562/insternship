"""Simple website scraper to extract emails and phone numbers from a business website."""
import re
import requests
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{6,}\d)")


def extract_contacts_from_website(url: str, timeout: int = 8):
    result = {"email": None, "phone": None, "contact_page": None}
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "LeadGenBot/1.0"})
        resp.raise_for_status()
        text = resp.text
        emails = set(EMAIL_RE.findall(text))
        phones = set(PHONE_RE.findall(text))
        if emails:
            result["email"] = list(emails)[0]
        if phones:
            result["phone"] = list(phones)[0]
        # Try to find a contact page link
        soup = BeautifulSoup(text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if "contact" in href or "iletisim" in href or "kontakt" in href:
                href_full = requests.compat.urljoin(url, a["href"])
                result["contact_page"] = href_full
                # try to fetch contact page for more emails
                try:
                    cresp = requests.get(href_full, timeout=timeout, headers={"User-Agent": "LeadGenBot/1.0"})
                    cresp.raise_for_status()
                    cemails = set(EMAIL_RE.findall(cresp.text))
                    if cemails and not result.get("email"):
                        result["email"] = list(cemails)[0]
                except Exception:
                    pass
                break
    except Exception:
        # Return partial results if available
        pass
    return result
