"""Outreach simulator: decides what to do with each lead and logs a status."""
import time
from random import random


def simulate_outreach(lead: dict):
    """Return status and message."""
    # Rules: if no email -> 'No email found'
    if not lead.get("email"):
        return {"status": "no_email", "message": "No email address found; queued for manual lookup."}
    # if rating exists and < 3.0 skip
    try:
        rating = float(lead.get("rating") or 0)
    except Exception:
        rating = 0
    if rating and rating < 3.0:
        return {"status": "skipped_low_rating", "message": f"Skipped due to low rating {rating}"}
    # Otherwise simulate queuing email
    time.sleep(0.2)
    if random() < 0.02:
        return {"status": "send_failed", "message": "Simulated send failure"}
    return {"status": "queued", "message": "Email queued for send"}
