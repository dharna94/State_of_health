import requests
import json

url = "http://127.0.0.1:5000/api/soh_calculation/soh/get_soh_details"

payload = json.dumps({
    "vins": ["MB7U8CLLFMJA30129", "MB7U8CLLFLJL31151"]
})

headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
