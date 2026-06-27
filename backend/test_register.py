import requests
url = "http://127.0.0.1:8000/register"
payload = {"email": "tester99@example.com", "password": "pwd", "full_name": "Test User"}
try:
    resp = requests.post(url, json=payload)
    print("Status:", resp.status_code)
    print("Body:", resp.text)
except Exception as e:
    print("Error:", e)
