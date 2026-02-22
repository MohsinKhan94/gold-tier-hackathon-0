import requests

url = "http://localhost:8069/jsonrpc"

payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "login",
        "args": ["ai_employee", "sherankhan666@gmail.com", "admin"]
    },
    "id": 1
}

response = requests.post(url, json=payload)
print(response.json())