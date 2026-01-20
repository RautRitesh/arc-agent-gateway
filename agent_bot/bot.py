import os
import requests
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
ARC_RPC_URL = os.getenv("ARC_RPC_URL", "https://rpc.testnet.arc.network")
AGENT_PRIVATE_KEY = os.getenv("AGENT_PRIVATE_KEY") # You must add this to .env!
API_URL = "http://127.0.0.1:8000/api/premium/"

# Setup Web3
w3 = Web3(Web3.HTTPProvider(ARC_RPC_URL))
account = w3.eth.account.from_key(AGENT_PRIVATE_KEY)

# --- 1. DEFINE AGENT STATE ---
class AgentState(TypedDict):
    status: str          # 'idle', 'needs_payment', 'success'
    invoice: dict        # The payment request from Django
    tx_hash: Optional[str] # The proof of payment
    data: Optional[dict]   # The final data received

# --- 2. NODE: CHECK API ---
def check_api_node(state: AgentState):
    print("\n🤖 AGENT: Attempting to fetch data...")
    
    headers = {}
    # If we have a hash, attach it!
    if state.get('tx_hash'):
        print(f"🎫 AGENT: Presenting receipt: {state['tx_hash'][:10]}...")
        headers['Authorization'] = f"Arc {state['tx_hash']}"
    
    try:
        response = requests.get(API_URL, headers=headers)
        
        if response.status_code == 200:
            print("✅ AGENT: Access Granted!")
            return {"status": "success", "data": response.json()}
            
        elif response.status_code == 402:
            print("⛔ AGENT: Hit Paywall (402). Analyzing invoice...")
            return {"status": "needs_payment", "invoice": response.json()['invoice']}
            
        else:
            print(f"❌ AGENT: Unexpected Error {response.status_code}")
            return {"status": "error"}
            
    except Exception as e:
        return {"status": "error", "data": str(e)}

# --- 3. NODE: MAKE PAYMENT ---
# --- 3. NODE: MAKE PAYMENT ---
def payment_node(state: AgentState):
    invoice = state['invoice']
    amount = invoice['amount']
    dest = invoice['destination_address']
    
    print(f"💸 AGENT: Decided to pay {amount} USDC to {dest}...")
    
    # Construct Transaction (Native USDC Transfer on Arc)
    tx = {
        'nonce': w3.eth.get_transaction_count(account.address),
        'to': dest,
        'value': w3.to_wei(amount, 'ether'), # 1.0 USDC
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'chainId': 5042002 
    }
    
    # Sign & Send
    signed_tx = w3.eth.account.sign_transaction(tx, AGENT_PRIVATE_KEY)
    
    # --- FIX IS HERE (Use snake_case) ---
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction) 
    hex_hash = w3.to_hex(tx_hash)
    
    print(f"🚀 AGENT: Payment Sent! Hash: {hex_hash}")
    
    # Wait for block confirmation (Crucial for Arc verification)
    print("⏳ AGENT: Waiting for block confirmation...")
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return {"tx_hash": hex_hash}
# --- 4. BUILD THE GRAPH ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("check_api", check_api_node)
workflow.add_node("pay_network", payment_node)

# Set Entry Point
workflow.set_entry_point("check_api")

# Define Logic
def decide_next_step(state):
    if state['status'] == 'needs_payment':
        return "pay_network"
    elif state['status'] == 'success':
        return END
    else:
        return END

workflow.add_conditional_edges(
    "check_api",
    decide_next_step
)

# Payment always loops back to check api
workflow.add_edge("pay_network", "check_api")

# Compile
app = workflow.compile()

# --- 5. RUN IT ---
if __name__ == "__main__":
    print("--- STARTING AUTONOMOUS COMMERCE AGENT ---")
    app.invoke({"status": "idle", "invoice": {}, "tx_hash": None})