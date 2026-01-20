import os
import requests
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from circle.web3 import utils
from circle.web3 import developer_controlled_wallets

load_dotenv()
API_URL = "http://127.0.0.1:8000/api/premium/"
DASHBOARD_URL = "http://127.0.0.1:8000/api/report-log/"

# Setup Circle
client = utils.init_developer_controlled_wallets_client(
    api_key=os.getenv("CIRCLE_API_KEY"),
    entity_secret=os.getenv("CIRCLE_ENTITY_SECRET")
)

# Use TransactionsApi for transaction-related operations
circle_api = developer_controlled_wallets.TransactionsApi(client)

class AgentState(TypedDict):
    status: str; invoice: dict; tx_hash: Optional[str]

def log(msg, type="info", tx_hash=None):
    print(msg)
    try: requests.post(DASHBOARD_URL, json={"message": msg, "type": type, "tx_hash": tx_hash})
    except: pass

def check_api(state):
    log("🤖 Agent connecting to Marketplace...", "info")
    headers = {'Authorization': f"Arc {state.get('tx_hash')}"} if state.get('tx_hash') else {}
    
    try:
        res = requests.get(API_URL, headers=headers)
        if res.status_code == 200:
            log("✅ PAYMENT ACCEPTED! Data Received.", "success", state.get('tx_hash'))
            return {"status": "success"}
        elif res.status_code == 402:
            log("⛔ 402 PAYWALL DETECTED. Analyzing Invoice...", "error")
            return {"status": "needs_payment", "invoice": res.json()['invoice']}
    except Exception as e:
        log(f"Error: {e}", "error")
        return {"status": "error"}

def pay_network(state):
    invoice = state['invoice']
    amount = str(invoice['amount'])
    dest = invoice['destination_address']
    
    log(f"💸 Authorizing Circle Wallet: Pay {amount} USDC...", "payment")
    
    try:
        # Create the request object with the correct class name
        # First, let's try to find the correct request class
        request = developer_controlled_wallets.CreateTransferTransactionForDeveloperRequest(
            wallet_id=os.getenv("CIRCLE_WALLET_ID"),
            token_id=os.getenv("USDC_TOKEN_ID"),
            destination_address=dest,
            amounts=[amount],
            fee_level="MEDIUM"
        )
        
        # Use the correct parameter name
        resp = circle_api.create_developer_transaction_transfer(
            create_transfer_transaction_for_developer_request=request
        )
        
        tx_id = resp.data.id
        log(f"🚀 Signed & Sent! Circle ID: {tx_id}", "payment")
        
        # Poll for Hash
        for i in range(10):
            time.sleep(2)
            tx = circle_api.get_transaction(id=tx_id).data.transaction
            if tx.tx_hash:
                log(f"🔗 On-Chain Hash Confirmed: {tx.tx_hash}", "payment")
                return {"tx_hash": tx.tx_hash}
            log("⏳ Waiting for Arc block confirmation...", "info")
            
        return {"status": "error"}
    except Exception as e:
        log(f"Payment Failed: {e}", "error")
        return {"status": "error"}
       
workflow = StateGraph(AgentState)
workflow.add_node("check", check_api)
workflow.add_node("pay", pay_network)
workflow.set_entry_point("check")
workflow.add_conditional_edges("check", lambda x: "pay" if x['status'] == "needs_payment" else END)
workflow.add_edge("pay", "check")
app = workflow.compile()

if __name__ == "__main__":
    app.invoke({"status": "idle", "invoice": {}, "tx_hash": None})