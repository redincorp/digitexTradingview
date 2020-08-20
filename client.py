import requests
import json
payload = {
    "exchange" : "ByBIT",
    "ticker" : "BTCUSD",
    "action" : "buy"
    }
server_url = "https://daffy-roomy-megaraptor.glitch.me/exchange/digitexfutures/testnet"
#local_host = "http://127.0.0.1:5000/exchange/digitexfutures/testnet"
response = requests.post(server_url, data = json.dumps(payload))

print(response.status_code, response.text)
