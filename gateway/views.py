from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, time
from utils_agent.agent import CircleAgent

agent_logs = []
payment_status = {"status": "LOCKED", "tx_hash": None}

def dashboard(request):
    """Renders the main monitoring dashboard"""
    return render(request, 'dashboard.html')

def start_agent(request):
    """Triggered by frontend to start the automated agent loop"""
    agent = CircleAgent()
    bot = agent()
    bot.invoke({"status": "idle", "invoice": {}, "tx_hash": None})
    return JsonResponse({"status": "finished"})

def premium_data(request):
    """
    Returns Institutional-Grade Market Intelligence.
    This data is protected by ArcPaywallMiddleware.
    """
    return JsonResponse({
        "status": "success",
        "data": {
            "title": "Arc Network Analytics Report",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": [
                {"label": "Total Value Locked", "value": "$14.2M", "trend": "+2.4%"},
                {"label": "24h Network Volume", "value": "$842,000", "trend": "-0.5%"},
                {"label": "Active AI Agents", "value": "1,242", "trend": "+12%"},
                {"label": "Avg Transaction Cost", "value": "0.002 USDC", "trend": "Stable"}
            ],
            "intelligence": "Liquidity concentration is increasing in USDC/ARC pools. High-frequency agents are currently seeing optimal execution speeds."
        }
    })

def get_logs(request):
    """Returns the last 20 logs and current payment status for polling"""
    return JsonResponse({"logs": agent_logs[-20:], "payment_status": payment_status})

@csrf_exempt
def report_log(request):
    """Endpoint for the agent to report its status back to the dashboard"""
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