import os
import json
from django.http import JsonResponse
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Connect to Arc Network
w3 = Web3(Web3.HTTPProvider(os.getenv("ARC_RPC_URL")))
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET")
PRICE = 0.1  # 1 USDC

class ArcPaywallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Standard middleware call - just pass the request along
        # The real work now happens in process_view
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before the view is executed.
        This is where we check if the view is tagged as 'paywalled'.
        """
        # 1. Check if the view function has the tag we set in the decorator
        if getattr(view_func, 'is_paywalled', False):
            
            # 2. Check for the Payment Header
            # Format: "Authorization: Arc <TX_HASH>"
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Arc '):
                return self.send_402_invoice()

            tx_hash = auth_header.split(' ')[1]

            # 3. Verify the Payment on Blockchain
            if self.verify_transaction(tx_hash):
                return None # Return None means "Continue to the view"
            else:
                return JsonResponse({'error': 'Payment invalid or pending'}, status=403)
        
        return None # Not a paywalled view, continue

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
        }, status=402)
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
            value_in_usdc = w3.from_wei(tx['value'], 'ether')
            
            if float(value_in_usdc) < PRICE:
                print(f"❌ Insufficient Amount: {value_in_usdc}")
                return False

            print(f"✅ Payment Verified: {tx_hash}")
            return True

        except Exception as e:
            print(f"Verification Error: {e}")
            return False