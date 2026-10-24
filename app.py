from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.json or {}
    query_type = data.get('type', 'username')
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'status': 'error', 'message': 'Target specified nahi hai'}), 400

    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    if query_type == 'username':
        # Real platform checks
        targets = [
            {"platform": "GitHub", "category": "Developer", "url": f"https://github.com/{query}", "icon": "github"},
            {"platform": "Reddit", "category": "Social Forum", "url": f"https://www.reddit.com/user/{query}", "icon": "reddit"},
            {"platform": "Pinterest", "category": "Media", "url": f"https://www.pinterest.com/{query}/", "icon": "pinterest"},
            {"platform": "Telegram", "category": "Messaging", "url": f"https://t.me/{query}", "icon": "telegram"},
            {"platform": "DockerHub", "category": "Developer", "url": f"https://hub.docker.com/v2/users/{query}", "icon": "docker"}
        ]

        for target in targets:
            try:
                # Real HTTP call to target website
                resp = requests.get(target["url"], headers=headers, timeout=5)
                if resp.status_code == 200:
                    status = "FOUND"
                    final_url = target["url"]
                else:
                    status = "NOT_FOUND"
                    final_url = ""
            except Exception:
                status = "NOT_FOUND"
                final_url = ""

            results.append({
                "platform": target["platform"],
                "category": target["category"],
                "status": status,
                "url": final_url,
                "icon": target["icon"]
            })

    elif query_type == 'email':
        # Basic Email MX / Domain OSINT check
        domain = query.split('@')[-1] if '@' in query else ''
        if domain:
            try:
                resp = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
                dns_data = resp.json()
                if dns_data.get("Status") == 0 and "Answer" in dns_data:
                    status = "FOUND"
                else:
                    status = "NOT_FOUND"
            except Exception:
                status = "NOT_FOUND"
        else:
            status = "NOT_FOUND"

        results.append({
            "platform": f"Mail Server ({domain})",
            "category": "MX Record Status",
            "status": status,
            "url": f"https://{domain}" if status == "FOUND" else "",
            "icon": "mail"
        })

    return jsonify({
        "status": "success",
        "query": query,
        "type": query_type,
        "data": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
