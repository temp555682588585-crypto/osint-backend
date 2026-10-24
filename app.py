from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/scan', methods=['POST'])
def handle_scan():
    data = request.json or {}
    query_type = data.get('type', 'username')
    query = data.get('query', '')

    if not query:
        return jsonify({'status': 'error', 'message': 'No target specified'}), 400

    results = [
        {
            "platform": "Instagram",
            "category": "Social Network",
            "status": "FOUND",
            "url": f"https://instagram.com/{query}",
            "icon": "instagram"
        },
        {
            "platform": "GitHub",
            "category": "Developer Community",
            "status": "FOUND",
            "url": f"https://github.com/{query}",
            "icon": "github"
        },
        {
            "platform": "Twitter",
            "category": "Social Network",
            "status": "NOT_FOUND",
            "url": "",
            "icon": "twitter"
        }
    ]

    return jsonify({
        "status": "success",
        "query": query,
        "type": query_type,
        "data": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
