import os
import requests
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from circle.web3 import utils, developer_controlled_wallets

load_dotenv()

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/premium/"
DASHBOARD_URL = "http://127.0.0.1:8000/api/report-log/"

class AgentState(TypedDict):
    status: str
    invoice: dict
    tx_hash: Optional[str]

class CircleAgent:
    def __init__(self):
        # Setup Circle Client
        self.client = utils.init_developer_controlled_wallets_client(
            api_key=os.getenv("CIRCLE_API_KEY"),
            entity_secret=os.getenv("CIRCLE_ENTITY_SECRET")
        )
        self.circle_api = developer_controlled_wallets.TransactionsApi(self.client)
        
        # Build the graph on initialization
        self.app = self._build_graph()

    def _log(self, msg, type="info", tx_hash=None):
        print(msg)
        try:
            requests.post(DASHBOARD_URL, json={"message": msg, "type": type, "tx_hash": tx_hash})
        except:
            pass

    def _check_api(self, state: AgentState):
        self._log("🤖 Agent connecting to Marketplace...", "info")
        headers = {'Authorization': f"Arc {state.get('tx_hash')}"} if state.get('tx_hash') else {}
        
        try:
            res = requests.get(API_URL, headers=headers)
            if res.status_code == 200:
                self._log("✅ PAYMENT ACCEPTED! Data Received.", "success", state.get('tx_hash'))
                return {"status": "success"}
            elif res.status_code == 402:
                self._log("⛔ 402 PAYWALL DETECTED. Analyzing Invoice...", "error")
                return {"status": "needs_payment", "invoice": res.json()['invoice']}
        except Exception as e:
            self._log(f"Error: {e}", "error")
            return {"status": "error"}

    def _pay_network(self, state: AgentState):
        invoice = state['invoice']
        amount = str(invoice['amount'])
        dest = invoice['destination_address']
        
        self._log(f"💸 Authorizing Circle Wallet: Pay {amount} USDC...", "payment")
        
        try:
            request = developer_controlled_wallets.CreateTransferTransactionForDeveloperRequest(
                wallet_id=os.getenv("CIRCLE_WALLET_ID"),
                token_id=os.getenv("USDC_TOKEN_ID"),
                destination_address=dest,
                amounts=[amount],
                fee_level="MEDIUM"
            )
            
            resp = self.circle_api.create_developer_transaction_transfer(
                create_transfer_transaction_for_developer_request=request
            )
            
            tx_id = resp.data.id
            self._log(f"🚀 Signed & Sent! Circle ID: {tx_id}", "payment")
            
            for i in range(10):
                time.sleep(2)
                tx = self.circle_api.get_transaction(id=tx_id).data.transaction
                if tx.tx_hash:
                    self._log(f"🔗 On-Chain Hash Confirmed: {tx.tx_hash}", "payment")
                    return {"tx_hash": tx.tx_hash}
                self._log("⏳ Waiting for Arc block confirmation...", "info")
                
            return {"status": "error"}
        except Exception as e:
            self._log(f"Payment Failed: {e}", "error")
            return {"status": "error"}

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("check", self._check_api)
        workflow.add_node("pay", self._pay_network)
        
        workflow.set_entry_point("check")
        
        workflow.add_conditional_edges(
            "check", 
            lambda x: "pay" if x['status'] == "needs_payment" else END
        )
        workflow.add_edge("pay", "check")
        
        return workflow.compile()

    def run(self, initial_state: Optional[AgentState] = None):
        """Standard method to invoke the agent"""
        if initial_state is None:
            initial_state = {"status": "idle", "invoice": {}, "tx_hash": None}
        return self.app.invoke(initial_state)

    def __call__(self, *args, **kwargs):
        """Allows calling the object directly like: agent()"""
        return self.app