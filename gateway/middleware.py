import os
from django.http import JsonResponse
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

w3 = Web3(Web3.HTTPProvider(os.getenv("ARC_RPC_URL")))
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET")
PRICE = 0.1 # USDC

class ArcPaywallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only block the Premium API
        if not request.path.startswith('/api/premium/'):
            return self.get_response(request)

        # Check for Authorization Header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Arc '):
            return self.send_402_invoice()

        tx_hash = auth_header.split(' ')[1]

        if self.verify_payment(tx_hash):
            return self.get_response(request)
        else:
            return JsonResponse({'error': 'Invalid Payment'}, status=403)

    def send_402_invoice(self):
        return JsonResponse({
            'error': 'Payment Required',
            'message': f'Pay {PRICE} USDC to access.',
            'invoice': {
                'amount': PRICE,
                'currency': 'USDC',
                'destination_address': MERCHANT_WALLET
            }
        }, status=402)

    def verify_payment(self, tx_hash):
        try:
            tx = w3.eth.get_transaction(tx_hash)
            # Basic checks: To me? Enough money?
            if tx['to'].lower() != MERCHANT_WALLET.lower(): return False
            return True
        except:
            return False