from django.contrib import admin
from django.urls import path
from gateway.views import premium_data, dashboard, get_logs, report_log, start_agent

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/premium/', premium_data),
    path('dashboard/', dashboard),
    # API Endpoints
    path('api/start-agent/', start_agent), # New endpoint for triggering the agent
    path('api/get-logs/', get_logs),
    path('api/report-log/', report_log),
]