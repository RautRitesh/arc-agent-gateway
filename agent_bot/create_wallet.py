import os
from circle.web3 import utils
from circle.web3 import developer_controlled_wallets
from dotenv import load_dotenv

load_dotenv()

client = utils.init_developer_controlled_wallets_client(
    api_key=os.getenv("CIRCLE_API_KEY"),
    entity_secret=os.getenv("CIRCLE_ENTITY_SECRET")
)
api = developer_controlled_wallets.DeveloperControlledWalletsApi(client)

try:
    print("Creating Wallet Set...")
    ws_req = developer_controlled_wallets.CreateWalletSetRequest.from_dict({"name": "Hackathon Set"})
    ws = api.create_wallet_set(ws_req).data.wallet_set
    
    print("Creating Wallet...")
    w_req = developer_controlled_wallets.CreateWalletsRequest.from_dict({
        "walletSetId": ws.id,
        "blockchains": ["ARC_TESTNET"],
        "count": 1,
        "metadata": [{"name": "Agent 1"}]
    })
    wallet = api.create_wallets(w_req).data.wallets[0]
    
    print("\n✅ COPY THESE TO YOUR .ENV FILE:")
    print(f"CIRCLE_WALLET_ID={wallet.id}")
    print(f"AGENT_ADDRESS={wallet.address}")
except Exception as e:
    print(f"Error: {e}")