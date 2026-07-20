"""OpenAI-based email generator wrapper"""
import os
import openai

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


def generate_email(business: dict, openai_api_key: str = None, model: str = None):
    """Return a dict with subject and body."""
    if openai_api_key is None:
        openai_api_key = os.environ.get("OPENAI_API_KEY")
    if model is None:
        model = OPENAI_MODEL
    openai.api_key = openai_api_key

    name = business.get("name") or "there"
    website = business.get("website") or ""
    rating = business.get("rating")
    email = business.get("email") or ""
    # Construct a prompt
    prompt = f"Write a short, friendly cold outreach email to {name}. The business website is {website}. The Google rating is {rating}. Try to identify likely pain points for a small local business and propose a clear single next step. Keep subject line under 8 words and body under 220 words. If email is missing, indicate that in the note."

    messages = [
        {"role": "system", "content": "You are a helpful assistant that writes personalized outreach emails for small businesses."},
        {"role": "user", "content": prompt},
    ]
    try:
        resp = openai.ChatCompletion.create(model=model, messages=messages, max_tokens=400, temperature=0.6)
        choice = resp.get("choices", [])[0]
        body = choice.get("message", {}).get("content", "")
    except Exception as e:
        body = f"[Error generating email: {e}]"
    # Very simple heuristic for subject
    subject = f"Quick idea for {name}"
    return {"subject": subject, "body": body, "note": ("no_email" if not email else "email_found")}
