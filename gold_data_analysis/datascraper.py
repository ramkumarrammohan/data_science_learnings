from websocket import create_connection
import json
import random
import string
import re
import pandas as pd
import csv
from datetime import datetime

def filter_raw_message(text):
    try:
        found1 = re.search('"m":"(.+?)",', text).group(1)
        found2 = re.search('"p":(.+?"}"])}', text).group(1)
        print(found1)
        print(found2)
        return found1, found2
    except AttributeError:
        print("error")
    

def generateSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "qs_" +random_string

def generateChartSession():
    stringLength=12
    letters = string.ascii_lowercase
    random_string= ''.join(random.choice(letters) for i in range(stringLength))
    return "cs_" +random_string

def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

def constructMessage(func, paramList):
    #json_mylist = json.dumps(mylist, separators=(',', ':'))
    return json.dumps({
        "m":func,
        "p":paramList
        }, separators=(',', ':'))

def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

def sendRawMessage(ws, message):
    ws.send(prependHeader(message))

def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

def generate_csv(a):
    out= re.search('"s":\[(.+?)\}\]', a).group(1)
    x=out.split(',{\"')
    
    with open('data_file.csv', mode='w', newline='') as data_file:
        employee_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        employee_writer.writerow(['index', 'date', 'open', 'high', 'low', 'close', 'volume'])
        
        for xi in x:
            xi= re.split('\[|:|,|\]', xi)
            print(xi)
            ind= int(xi[1])
            ts= datetime.fromtimestamp(float(xi[4])).strftime("%Y/%m/%d, %H:%M:%S")
            employee_writer.writerow([ind, ts, float(xi[5]), float(xi[6]), float(xi[7]), float(xi[8]), float(xi[9])])
            


# Initialize the headers needed for the websocket connection
headers = json.dumps({
    # 'Connection': 'upgrade',
    # 'Host': 'data.tradingview.com',
    'Origin': 'https://data.tradingview.com'
    # 'Cache-Control': 'no-cache',
    # 'Upgrade': 'websocket',
    # 'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    # 'Sec-WebSocket-Key': '2C08Ri6FwFQw2p4198F/TA==',
    # 'Sec-WebSocket-Version': '13',
    # 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.56',
    # 'Pragma': 'no-cache',
    # 'Upgrade': 'websocket'
})

    
# Then create a connection to the tunnel
ws = create_connection(
    'wss://data.tradingview.com/socket.io/websocket',headers=headers)

session= generateSession()
print("session generated {}".format(session))

chart_session= generateChartSession()
print("chart_session generated {}".format(chart_session))

# Then send a message through the tunnel 
sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
sendMessage(ws, "chart_create_session", [chart_session, ""])
# sendMessage(ws, "quote_create_session", [session])
# sendMessage(ws,"quote_set_fields", [session,"ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
# sendMessage(ws, "quote_add_symbols",[session, "NASDAQ:AAPL", {"flags":['force_permission']}])
# sendMessage(ws, "quote_fast_symbols", [session,"NASDAQ:AAPL"])

sendMessage(ws, "resolve_symbol", [chart_session,"symbol_1","={\"symbol\":\"NASDAQ:AAPL\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", "1", 1000])

# Printing all the result
a=""
while True:
    try:
        result = ws.recv()
        print(result)
        a=a+result+"\n"
    except Exception as e:
        print(e)
        break
    
generate_csv(a)