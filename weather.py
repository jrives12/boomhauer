import urllib.request
import json

base_url = "https://api.openweathermap.org/data/3.0/onecall"
api_key = ""#input("API_KEY: ")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}
params = {
        "lat" : "32.815417",#float(input("Latitude: "))
        "lon" : "-79.931889",#float(input("Longitude: "))
        "appid" : api_key
        }
        

request_url = f"{base_url}?{urllib.parse.urlencode(params)}" 

req = urllib.request.Request(request_url)

with urllib.request.urlopen(req) as response:
    data = response.read()
    encoding = response.info().get_content_charset('utf-8')
    result = json.loads(data.decode(encoding))

k = float(result['current']['temp'])
c = k - 273.15
f = (9/5) * c + 32
print("Temp (F): %.2f" % f)
