import re

def extract_urls(text: str):
    """
    Extract URLs/domains from a given text.
    Returns a list of normalized URLs found.
    """
    if not text:
        return []

    # Regex pattern for URLs (http, https, www)
    url_pattern = re.compile(r'(https?://[^\s]+|www\.[^\s]+)', re.IGNORECASE)
    urls = url_pattern.findall(text)

    # Normalize URLs: strip trailing punctuation, lowercase domains
    cleaned_urls = []
    for url in urls:
        url = url.rstrip('.,;!?')
        url = url.lower()
        cleaned_urls.append(url)

    return cleaned_urls
