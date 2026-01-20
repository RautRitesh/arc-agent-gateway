from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import time

# --- IN-MEMORY STORAGE ---
agent_logs = []
payment_status = {"status": "LOCKED", "tx_hash": None}

def dashboard(request):
    return render(request, 'dashboard.html')

def premium_data(request):
    """The Protected Content"""
    return JsonResponse({
        "status": "success", 
        "data": {
            "prediction": "Bitcoin -> $100k",
            "confidence": "99.9%",
            "secret_code": "ARC_WINNER_2025"
        }
    })

def get_logs(request):
    """Frontend Polling"""
    return JsonResponse({
        "logs": agent_logs[-20:], 
        "payment_status": payment_status
    })

@csrf_exempt
def report_log(request):
    """Agent Reporting"""
    if request.method == 'POST':
        data = json.loads(request.body)
        log_entry = {
            "message": data.get("message"),
            "type": data.get("type", "info"),
            "time": time.strftime("%H:%M:%S")
        }
        agent_logs.append(log_entry)
        
        if data.get("type") == "success":
            payment_status["status"] = "UNLOCKED"
            payment_status["tx_hash"] = data.get("tx_hash")
            
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"})