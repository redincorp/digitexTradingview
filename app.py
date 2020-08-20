from flask import Flask, request, Response
from websocket import create_connection
import json
import random
import string
import logging

logging.basicConfig(filename="digitexfutures-bot.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Order Handler for DigitexFutures from Tradingview Signal'

@app.route('/exchange/digitexfutures/testnet', methods=['POST'])
def exchange_digitexfutures_testnet():
    if request.method == 'POST':
        try:
            Testnet_API_URL = "wss://ws.tapi.digitexfutures.com"
            Testnet_API_Key = "a0350058883726160443b24c3e71da134f8fc6ec"
            statusFlag = False
            Data = request.data
            JSONData = json.loads(Data.decode('utf-8'))
            symbol = "{}-PERP".format(JSONData["ticker"])
            side = JSONData["action"]
            ws = create_connection(Testnet_API_URL)
            payload = {
                "id" : 1,
                "method" : "auth",
                "params" :
                {
                    "type" : "token",
                    "value" : Testnet_API_Key
                    }
                }
            ws.send(json.dumps(payload))
            while True:
                data = ws.recv()
                if data != "ping":
                    jdata = json.loads(data)
                    if "id" in jdata:
                        if jdata["id"] == 1:
                            if jdata["status"] == "ok":
                                logger.debug("{}".format(jdata["status"]))
                                statusFlag = True
                            if jdata["status"] == "error":
                                logger.debug("{}, {} : {}".format(jdata["status"], jdata["code"], jdata["msg"]))
                                statusFlag = False
                    if "ch" in jdata:
                        if jdata["ch"] == "tradingStatus":
                            if statusFlag == True:
                                logger.debug("{}, {}".format(jdata["ch"], jdata["data"]["available"]))
                                alphanumeric = string.ascii_letters + "0123456789"
                                orderID = ''.join(random.choice(alphanumeric) for i in range(16))
                                payload = {
                                    "id":2,
                                    "method":"placeOrder",
                                    "params":
                                    {
                                        "symbol" : symbol.upper(),
                                        "clOrdId" : orderID,
                                        "ordType" : "MARKET",
                                        "timeInForce" : "IOC",
                                        "side": side.upper(),
                                        "px": 0,
                                        "qty": 1
                                        }
                                    }
                                ws.send(json.dumps(payload))
                            if statusFlag == False:
                                logger.debug("{}, {}".format(jdata["ch"], jdata["data"]["available"]))
                                ws.close(False)
                        if jdata["ch"] == "orderStatus":
                            logger.debug("{}, {} : {}".format(jdata["ch"], jdata["data"]["symbol"], jdata["data"]["orderStatus"]))
                            ws.close()
                        if jdata["ch"] == "orderFilled":
                            logger.debug("{}, {} : {}".format(jdata["ch"], jdata["data"]["symbol"], jdata["data"]["orderStatus"]))
                            ws.close()
                        if jdata["ch"] == "error":
                            logger.debug("{}, {} : {}".format(jdata["ch"], jdata["data"]["code"], jdata["data"]["msg"]))
                            ws.close()
            else:
                logger.debug("{}".format(data))
        except:
            logger.debug("DigitexFutures: Connection was closed...")
        finally:
            logger.debug("DigitexFutures: BOT Execution was completed")
            responseData = {
                "status" : True
                }
            return Response(json.dumps(responseData), status=200, mimetype='application/json')
    else:
        responseData = {
            "status" : False
            }
        return Response(json.dumps(responseData), status=404, mimetype='application/json')

if __name__ == '__main__':
   app.run()
