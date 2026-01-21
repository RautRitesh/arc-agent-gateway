import os
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("CIRCLE_API_KEY")
wallet_id = os.getenv("CIRCLE_WALLET_ID")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# This endpoint fetches balances for your specific wallet. 
# The response includes the system UUID (Token ID) for every token in the wallet.
url = f"https://api.circle.com/v1/w3s/wallets/{wallet_id}/balances"

print(f"Checking balances for Wallet ID: {wallet_id}...")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    token_balances = response.json().get('data', {}).get('tokenBalances', [])
    
    if not token_balances:
        print("\n⚠️ No tokens found in this wallet.")
        print("Tip: Use the Arc Testnet Faucet (faucet.circle.com) to send USDC to your AGENT_ADDRESS.")
    else:
        print("\n=== Available Tokens ===")
        for item in token_balances:
            token = item.get('token', {})
            print(f"Symbol: {token.get('symbol')}")
            print(f"Token ID: {token.get('id')}  <-- COPY THIS")
            print(f"Balance: {item.get('amount')}")
            print(f"Blockchain: {token.get('blockchain')}")
            print("-" * 50)
else:
    print(f"Error: {response.status_code}")
    print(response.text)