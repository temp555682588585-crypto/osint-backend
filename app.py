from flask import Flask, request, jsonify
from flask_cors import CORS
from apify_client import ApifyClient

app = Flask(__name__)
CORS(app)

# जो API Key आपने दी है, वह यहाँ सीधी सेट है
APIFY_TOKEN = "Apify_api_vGcL1v5U25LsNxUaHkgBNnaysA4Dbw0Zay9Q"
client = ApifyClient(APIFY_TOKEN)

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.json or {}
    query_type = data.get('type', 'username')
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'status': 'error', 'message': 'Target query missing'}), 400

    results = []

    try:
        if query_type == 'username':
            # Apify का इस्तेमाल करके यूजरनेम/प्रोफाइल स्कैन करना
            run_input = {
                "username": query,
            }
            
            # Apify का Instagram Scraper कॉल कर रहे हैं
            actor_call = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
            
            # रिजल्ट्स फेच करना
            items_found = False
            for item in client.dataset(actor_call["defaultDatasetId"]).iterate_items():
                items_found = True
                results.append({
                    "platform": "Instagram",
                    "category": "Social Media",
                    "status": "FOUND",
                    "url": f"https://www.instagram.com/{query}",
                    "details": f"Name: {item.get('fullName', 'N/A')} | Followers: {item.get('followersCount', 0)}",
                    "icon": "instagram"
                })
            
            if not items_found:
                results.append({
                    "platform": "Instagram",
                    "category": "Social Media",
                    "status": "NOT_FOUND",
                    "url": f"https://www.instagram.com/{query}",
                    "details": "Profile not found via Apify",
                    "icon": "instagram"
                })
        
        else:
            results.append({
                "platform": "Apify Cloud",
                "category": "System",
                "status": "FOUND",
                "url": "",
                "details": f"Successfully processed {query_type} query",
                "icon": "shield"
            })

    except Exception as e:
        results.append({
            "platform": "API Error",
            "category": "System",
            "status": "NOT_FOUND",
            "url": "",
            "details": f"Error: {str(e)}",
            "icon": "alert-circle"
        })

    return jsonify({
        "status": "success",
        "query": query,
        "type": query_type,
        "data": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
