from django.shortcuts import render
from django.http import JsonResponse
from functools import wraps

# Custom Decorator to mark views as "Paid"
def payment_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # We don't need to set anything on 'request' here anymore
        return view_func(request, *args, **kwargs)
    
    # Tag the function object itself so Middleware can see it efficiently
    _wrapped_view.is_paywalled = True 
    return _wrapped_view

@payment_required
def premium_data(request):
    """
    This data is expensive! Only paid agents can see it.
    """
    return JsonResponse({
        "status": "success",
        "data": {
            "prediction": "Bitcoin will reach 100k",
            "confidence": "99%",
            "secret_code": "ARC_WINNER_2025"
        }
    })

def home(request):
    """Simple check to see if server is running"""
    return JsonResponse({"status": "Arc Gateway Online"})