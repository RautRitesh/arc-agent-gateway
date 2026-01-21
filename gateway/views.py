from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, time
from utils_agent.agent import CircleAgent

agent_logs = []
payment_status = {"status": "LOCKED", "tx_hash": None}

def dashboard(request):
    return render(request, 'dashboard.html')

def start_agent(request):
    """Triggered by frontend to prevent page hang"""
    agent = CircleAgent()
    bot = agent()
    bot.invoke({"status": "idle", "invoice": {}, "tx_hash": None})
    return JsonResponse({"status": "finished"})

def premium_data(request):
    """Returns Institutional-Grade Financial Audit Data"""
    return JsonResponse({
        "status": "success",
        "data": {
            "report_id": "ARC-AUDIT-992",
            "asset": "USDC/ARC Liquidity Pool",
            "risk_score": "2.1 (Low Risk)",
            "tvl_verified": "$1,240,500.00",
            "slippage_analysis": "0.04% for $10k swap",
            "health_factor": "98.5%",
            "last_audit": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    })

def get_logs(request):
    return JsonResponse({"logs": agent_logs[-20:], "payment_status": payment_status})

@csrf_exempt
def report_log(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        agent_logs.append({
            "message": data.get("message"),
            "type": data.get("type", "info"),
            "time": time.strftime("%H:%M:%S")
        })
        if data.get("type") == "success":
            payment_status["status"] = "UNLOCKED"
            payment_status["tx_hash"] = data.get("tx_hash")
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error"})