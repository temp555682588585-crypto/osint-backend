
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def check_github(username):
    url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "platform": "GitHub",
                "category": "Developer Community",
                "status": "FOUND",
                "url": data.get("html_url"),
                "details": f"Public Repos: {data.get('public_repos')}, Followers: {data.get('followers')}",
                "icon": "github"
            }
    except Exception:
        pass
    return {"platform": "GitHub", "category": "Developer Community", "status": "NOT_FOUND", "url": "", "icon": "github"}

def check_reddit(username):
    url = f"https://www.reddit.com/user/{username}/about.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code == 200:
            data = r.json().get("data", {})
            return {
                "platform": "Reddit",
                "category": "Social Forum",
                "status": "FOUND",
                "url": f"https://www.reddit.com/user/{username}",
                "details": f"Karma: {data.get('total_karma', 0)}",
                "icon": "reddit"
            }
    except Exception:
        pass
    return {"platform": "Reddit", "category": "Social Forum", "status": "NOT_FOUND", "url": "", "icon": "reddit"}

def check_telegram(username):
    url = f"https://t.me/s/{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        # Telegram channel/user public preview check
        if r.status_code == 200 and "tgme_page_title" in r.text and "If you have Telegram" in r.text:
            return {
                "platform": "Telegram",
                "category": "Messaging",
                "status": "FOUND",
                "url": f"https://t.me/{username}",
                "details": "Public Profile / Channel Active",
                "icon": "telegram"
            }
    except Exception:
        pass
    return {"platform": "Telegram", "category": "Messaging", "status": "NOT_FOUND", "url": "", "icon": "telegram"}

def check_email_gravatar(email):
    import hashlib
    email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
    url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return {
                "platform": "Gravatar / WordPress",
                "category": "Email Identity",
                "status": "FOUND",
                "url": f"https://www.gravatar.com/{email_hash}",
                "details": "Registered Profile Image Found",
                "icon": "mail"
            }
    except Exception:
        pass
    return {"platform": "Gravatar", "category": "Email Identity", "status": "NOT_FOUND", "url": "", "icon": "mail"}

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.json or {}
    query_type = data.get('type', 'username')
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'status': 'error', 'message': 'Target enter karo'}), 400

    results = []

    if query_type == 'username':
        results.append(check_github(query))
        results.append(check_reddit(query))
        results.append(check_telegram(query))

    elif query_type == 'email':
        results.append(check_email_gravatar(query))
        # MX record check for real email validity
        domain = query.split('@')[-1] if '@' in query else ''
        if domain:
            try:
                r = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
                dns_res = r.json()
                if dns_res.get("Status") == 0 and "Answer" in dns_res:
                    results.append({
                        "platform": f"Mail Domain ({domain})",
                        "category": "MX DNS Status",
                        "status": "FOUND",
                        "url": f"https://{domain}",
                        "details": "Valid Mail Server Active",
                        "icon": "mail"
                    })
            except Exception:
                pass

    return jsonify({
        "status": "success",
        "query": query,
        "type": query_type,
        "data": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
