from flask import Flask, render_template, request
import requests
import json
from typing import NamedTuple


app = Flask(__name__, template_folder='.')

HEADERS = {'Content-type':'application/json'}
RPC_ENDPOINT = 'https://solana-mainnet.phantom.tech'
LAMPORT_TO_SOL = 0.000000001

class Transaction(NamedTuple):
    fees: float
    success: bool

class Resp(NamedTuple):
    sol_fees: float
    sol_fees_usd: float
    fail_count: float
    fail_cost_usd: float
    avg_transaction_cost: float
    num_transactions: float
    failed: bool

FAILED_RESP = Resp(0,0,0,0,0,0,True)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/getfees", methods=['GET'])
def get_fees():
    try:
        address = request.args.get('a')
        sol_usd = get_sol_price()
   
        transactions = request_transactions(address)

        if(len(transactions) == 0):
            return json.dumps(Resp(
                sol_fees=0,
                sol_fees_usd=0,
                fail_count=0,
                fail_cost_usd=0,
                avg_transaction_cost=0,
                num_transactions=0,
                failed=False
            )._asdict())
        
        fees = request_fees(transactions)

        total_fees_lamports = sum([i.fees for i in fees])
        total_fees_usd = lamports_to_usd(total_fees_lamports, sol_usd)

        failed_fees = [i.fees for i in fees if not i.success]
        failed_fees_usd = lamports_to_usd(sum(failed_fees), sol_usd)

        resp = Resp(
            sol_fees=total_fees_lamports,
            sol_fees_usd=truncate(total_fees_usd, 4),
            fail_count=len(failed_fees),
            fail_cost_usd=truncate(failed_fees_usd, 4),
            avg_transaction_cost=truncate(total_fees_lamports / len(transactions), 4),
            num_transactions=len(transactions),
            failed=False
        )

        return json.dumps(resp._asdict())
    except Exception as e:
        print(e)
        return json.dumps(FAILED_RESP._asdict())

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def lamports_to_usd(lamports, sol_usd):
    return lamports * LAMPORT_TO_SOL * sol_usd

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
        fee = i['result']['meta']['fee']
        err = i['result']['meta']['err'] == None
        fees.append(Transaction(fee, err))

    print(fees)
    return fees

def get_sol_price():
    r = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT')
    return float(r.json()['price'])