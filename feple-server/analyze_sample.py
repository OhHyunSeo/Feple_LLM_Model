import requests

url = "http://127.0.0.1:8000/api/consultlytics/analyze/CALL_001/"
response = requests.get(url)
if response.status_code == 200:
    print(response.json())
else:
    print("API 호출 실패:", response.status_code, response.text) 