from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

@app.route('/google_places/address', methods=['GET'])
def get_company_address():
    print("Sending requests")
    company = request.args.get('company')
    location_str = request.args.get('locationStr')

    if not company or not location_str:
        return 'Missing required query parameters', 400

    query = f"{company}, {location_str}"
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={query}&inputtype=textquery&fields=name,formatted_address&key={GOOGLE_API_KEY}"

    response = requests.get(url)
    data = response.json()
    print(data)
    
    if 'candidates' in data and data['candidates']:
        result = data['candidates'][0]
        return jsonify({'address': result.get('formatted_address')})
    else:
        return 'No results found', 404
if __name__ == '__main__':
    app.run(port=5002)