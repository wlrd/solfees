from flask import Flask, render_template, request
import requests 

app = Flask(__name__, template_folder='.')

HEADERS = {'Content-type':'application/json'}
RPC_ENDPOINT = 'https://solana-mainnet.phantom.tech'
LAMPORT_TO_SOL = 0.000000001

@app.route("/")
def index():
    print('in index')
    return render_template('index.html')

@app.route("/getfees", methods=['GET'])
def get_fees():
    addy = request.args.get('addy')
    print(addy)
    transactions = request_transactions(addy)
    print(transactions)
    total_fees = request_fees(transactions)
    sol_usd = get_sol_price()

    gas_spent = total_fees * LAMPORT_TO_SOL * sol_usd
    return str(gas_spent) + "USD"

def request_transactions(addy):
    getConfirmedSignaturesForAddress2 = f'''
    {{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getConfirmedSignaturesForAddress2",
    "params": [
        "{addy}"
    ]
    }}
    '''.strip()
    r = requests.post(RPC_ENDPOINT, data=getConfirmedSignaturesForAddress2, headers=HEADERS)
    transactions = [i['signature'] for i in r.json()['result']]
    return transactions

def request_fees(transactions):
    fees = []
    getConfirmedTransaction = '['
    for cnt, transaction in enumerate(transactions):
        getConfirmedTransaction += f'''
            {{
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getConfirmedTransaction",
            "params": [
                "{transaction}"
            ]
            }}
        '''.strip()
        if cnt != len(transactions) - 1:
            getConfirmedTransaction += ','
    getConfirmedTransaction += ']'   

    r = requests.post(RPC_ENDPOINT, data=getConfirmedTransaction, headers=HEADERS)
    for i in r.json():
        fees.append(i['result']['meta']['fee'])

    print(fees)
    return sum(fees)

def get_sol_price():
    r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT')
    return float(r.json()['price'])