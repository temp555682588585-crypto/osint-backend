from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import hashlib
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

app = Flask(__name__)
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ==================== 1. USERNAME PROFILING ====================
def handle_username_scan(username):
    platforms = [
        {"name": "GitHub", "category": "Developer", "url": f"https://api.github.com/users/{username}", "profile": f"https://github.com/{username}", "icon": "github"},
        {"name": "Reddit", "category": "Forum", "url": f"https://www.reddit.com/user/{username}/about.json", "profile": f"https://www.reddit.com/user/{username}", "icon": "reddit"},
        {"name": "Telegram", "category": "Messaging", "url": f"https://t.me/s/{username}", "profile": f"https://t.me/{username}", "icon": "telegram"},
        {"name": "Pinterest", "category": "Media", "url": f"https://www.pinterest.com/{username}/", "profile": f"https://www.pinterest.com/{username}/", "icon": "pinterest"},
        {"name": "Twitter / X", "category": "Social", "url": f"https://twitter.com/{username}", "profile": f"https://twitter.com/{username}", "icon": "twitter"},
        {"name": "Instagram", "category": "Social", "url": f"https://www.instagram.com/{username}/", "profile": f"https://www.instagram.com/{username}/", "icon": "instagram"}
    ]

    results = []
    for p in platforms:
        status = "NOT_FOUND"
        details = "Profile inactive or private"
        final_url = ""

        try:
            res = requests.get(p["url"], headers=HEADERS, timeout=5)
            if p["name"] == "GitHub" and res.status_code == 200:
                status = "FOUND"
                data = res.json()
                details = f"Public Repos: {data.get('public_repos', 0)} | Followers: {data.get('followers', 0)} | Name: {data.get('name', 'N/A')}"
                final_url = p["profile"]
            elif p["name"] == "Reddit" and res.status_code == 200 and "data" in res.json():
                status = "FOUND"
                karma = res.json().get("data", {}).get("total_karma", 0)
                details = f"Reddit Karma Active: {karma}"
                final_url = p["profile"]
            elif p["name"] == "Telegram" and res.status_code == 200 and "tgme_page_title" in res.text:
                status = "FOUND"
                details = "Public Telegram Account/Channel Reachable"
                final_url = p["profile"]
            elif res.status_code == 200:
                status = "FOUND"
                details = "Profile page accessible"
                final_url = p["profile"]
        except Exception:
            status = "NOT_FOUND"

        results.append({
            "platform": p["name"],
            "category": p["category"],
            "status": status,
            "url": final_url,
            "details": details,
            "icon": p["icon"]
        })
    return results

# ==================== 2. EMAIL PROFILING ====================
def handle_email_scan(email):
    email_clean = email.strip().lower()
    email_hash = hashlib.md5(email_clean.encode('utf-8')).hexdigest()
    results = []

    # Gravatar Identity Check
    try:
        g_res = requests.get(f"https://www.gravatar.com/avatar/{email_hash}?d=404", timeout=4)
        if g_res.status_code == 200:
            results.append({
                "platform": "Gravatar Global Profile",
                "category": "Identity & Avatar",
                "status": "FOUND",
                "url": f"https://www.gravatar.com/{email_hash}",
                "details": "Linked WordPress/Gravatar account found with avatar image",
                "icon": "mail"
            })
        else:
            results.append({
                "platform": "Gravatar Global Profile",
                "category": "Identity & Avatar",
                "status": "NOT_FOUND",
                "url": "",
                "details": "No global profile avatar registered for this email",
                "icon": "mail"
            })
    except Exception:
        pass

    # Domain & MX Check
    domain = email_clean.split('@')[-1] if '@' in email_clean else ''
    if domain:
        try:
            dns_res = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=4).json()
            if dns_res.get("Status") == 0 and "Answer" in dns_res:
                results.append({
                    "platform": f"Mail Server Domain ({domain})",
                    "category": "MX DNS Record",
                    "status": "FOUND",
                    "url": f"https://{domain}",
                    "details": f"Active mail exchange server provider verified for {domain}",
                    "icon": "mail"
                })
        except Exception:
            pass

    return results

# ==================== 3. PHONE NUMBER TO APP LINKING ====================
def handle_phone_scan(phone_str):
    results = []
    try:
        parsed_number = phonenumbers.parse(phone_str)
        is_valid = phonenumbers.is_valid_number(parsed_number)
        
        if is_valid:
            country = geocoder.description_for_number(parsed_number, "en")
            carrier_name = carrier.name_for_number(parsed_number, "en")
            formatted_intl = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            clean_digits = "".join(filter(str.isdigit, phone_str))

            # Telecom Core Info
            results.append({
                "platform": "Telecom Intelligence",
                "category": "Carrier & Region",
                "status": "FOUND",
                "url": "",
                "details": f"Country/Region: {country or 'Global'} | Carrier: {carrier_name or 'Private/Ported Operator'} | Format: {formatted_intl}",
                "icon": "phone"
            })

            # App Account Direct Links Mapping
            results.append({
                "platform": "WhatsApp Account Link",
                "category": "Messaging App",
                "status": "FOUND",
                "url": f"https://wa.me/{clean_digits}",
                "details": "Direct click-to-chat API profile link generated",
                "icon": "message-circle"
            })

            results.append({
                "platform": "Telegram Direct Link",
                "category": "Messaging App",
                "status": "FOUND",
                "url": f"https://t.me/{clean_digits}",
                "details": "Direct Telegram contact lookup link generated",
                "icon": "telegram"
            })

            results.append({
                "platform": "Truecaller / Caller Lookup",
                "category": "Directory Search",
                "status": "FOUND",
                "url": f"https://www.truecaller.com/search/in/{clean_digits}",
                "details": "External directory search reference link generated",
                "icon": "search"
            })
        else:
            results.append({
                "platform": "Telecom Intelligence",
                "category": "Validation",
                "status": "NOT_FOUND",
                "url": "",
                "details": "Invalid phone number structure. Use international format (e.g., +919876543210)",
                "icon": "phone"
            })
    except Exception:
        results.append({
            "platform": "Telecom Intelligence",
            "category": "Error",
            "status": "NOT_FOUND",
            "url": "",
            "details": "Error parsing number. Please include country code (+ prefix).",
            "icon": "phone"
        })
        
    return results

# ==================== MAIN API ROUTE ====================
@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.json or {}
    query_type = data.get('type', 'username')
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'status': 'error', 'message': 'Target query is empty'}), 400

    results = []

    if query_type == 'username':
        results = handle_username_scan(query)
    elif query_type == 'email':
        results = handle_email_scan(query)
    elif query_type == 'phone':
        results = handle_phone_scan(query)
    else:
        return jsonify({'status': 'error', 'message': 'Invalid query type'}), 400

    return jsonify({
        "status": "success",
        "query": query,
        "type": query_type,
        "data": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        
