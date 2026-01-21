import os
from dotenv import load_dotenv
from circle.web3 import utils
from circle.web3 import developer_controlled_wallets

load_dotenv()

client = utils.init_developer_controlled_wallets_client(
    api_key=os.getenv("CIRCLE_API_KEY"),
    entity_secret=os.getenv("CIRCLE_ENTITY_SECRET")
)

wallet_sets_api = developer_controlled_wallets.WalletSetsApi(client)
wallets_api = developer_controlled_wallets.WalletsApi(client)

try:
    print("Creating Wallet Set...")
    ws_req = developer_controlled_wallets.CreateWalletSetRequest.from_dict({
        "name": "Hackathon Set"
    })

    ws_response = wallet_sets_api.create_wallet_set(ws_req)
    
    # Access the actual_instance to get the DeveloperWalletSet object
    wallet_set = ws_response.data.wallet_set.actual_instance
    
    print("Wallet Set ID:", wallet_set.id)

    print("Creating Wallet...")
    w_req = developer_controlled_wallets.CreateWalletRequest.from_dict({
        "walletSetId": wallet_set.id,
        "blockchains": ["ARC-TESTNET"],  # Changed underscore to hyphen
        "metadata": [{"key": "name", "value": "Agent 1"}]
    })

    wallet_response = wallets_api.create_wallet(w_req)
    
    # The wallet might also be wrapped, so access actual_instance if needed
    wallet_data = wallet_response.data.wallets[0]
    if hasattr(wallet_data, 'actual_instance'):
        wallet = wallet_data.actual_instance
    else:
        wallet = wallet_data

    print("\n✅ COPY THESE TO YOUR .ENV FILE:")
    print(f"CIRCLE_WALLET_ID={wallet.id}")
    print(f"AGENT_ADDRESS={wallet.address}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()