import os
import json
from django.http import JsonResponse
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Connect to Arc Network
w3 = Web3(Web3.HTTPProvider(os.getenv("ARC_RPC_URL")))
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET")
PRICE = 1.0  # 1 USDC

class ArcPaywallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Check if the view demands payment
        if not getattr(request, 'is_paywalled', False):
            return self.get_response(request)

        # 2. Check for the Payment Header
        # Format: "Authorization: Arc <TX_HASH>"
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Arc '):
            return self.send_402_invoice()

        tx_hash = auth_header.split(' ')[1]

        # 3. Verify the Payment on Blockchain
        if self.verify_transaction(tx_hash):
            return self.get_response(request)
        else:
            return JsonResponse({'error': 'Payment invalid or pending'}, status=403)

    def send_402_invoice(self):
        """Returns the HTTP 402 Error with payment instructions."""
        response = JsonResponse({
            'error': 'Payment Required',
            'message': 'To access this API, pay 1.0 USDC on Arc Testnet.',
            'invoice': {
                'amount': PRICE,
                'currency': 'USDC',
                'chain': 'Arc Testnet',
                'chain_id': 5042002,  # Arc Chain ID
                'destination_address': MERCHANT_WALLET
            }
        }, status=402) #
        return response

    def verify_transaction(self, tx_hash):
        try:
            # Fetch transaction from Arc
            tx = w3.eth.get_transaction(tx_hash)
            
            # CRITICAL CHECK 1: Is it to ME?
            if tx['to'].lower() != MERCHANT_WALLET.lower():
                print("❌ Payment sent to wrong address")
                return False

            # CRITICAL CHECK 2: Is it enough USDC?
            # On Arc, USDC is the "native gas", so we check the 'value' field.
            # 'value' is in Wei (1 USDC = 10^18 Wei on Arc typically, or 10^6 depending on implementation)
            # Standard Arc Testnet uses 18 decimals for native USDC gas.
            value_in_usdc = w3.from_wei(tx['value'], 'ether')
            
            if float(value_in_usdc) < PRICE:
                print(f"❌ Insufficient Amount: {value_in_usdc}")
                return False

            print(f"✅ Payment Verified: {tx_hash}")
            return True

        except Exception as e:
            print(f"Verification Error: {e}")
            return False