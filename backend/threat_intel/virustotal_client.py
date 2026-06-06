import requests
from backend.config import VIRUSTOTAL_API_KEY

API_URL = "https://www.virustotal.com/api/v3/urls"

def check_url_reputation(url: str) -> dict:
    """
    Query VirusTotal API for a given URL.
    Returns verdict and reputation details.
    """
    if not VIRUSTOTAL_API_KEY:
        return {
            "url": url,
            "verdict": "unknown",
            "error": "Missing VirusTotal API key"
        }

    headers = {"x-apikey": VIRUSTOTAL_API_KEY}

    try:
        # Encode URL for VirusTotal
        url_id = requests.utils.quote(url, safe='')
        response = requests.get(f"{API_URL}/{url_id}", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)

            if malicious > 0 or suspicious > 0:
                verdict = "malicious"
            else:
                verdict = "safe"

            return {
                "url": url,
                "verdict": verdict,
                "stats": stats
            }
        else:
            return {
                "url": url,
                "verdict": "unknown",
                "error": f"API error {response.status_code}: {response.text}"
            }
    except Exception as e:
        # --- Heuristic fallback when API fails ---
        suspicious_keywords = ["login", "verify", "secure-update", "password", "account"]
        heuristic_verdict = "safe"
        if any(word in url.lower() for word in suspicious_keywords):
            heuristic_verdict = "malicious"

        return {
            "url": url,
            "verdict": heuristic_verdict,
            "error": f"Request failed: {e} (heuristic applied)"
        }
