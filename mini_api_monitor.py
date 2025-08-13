import time
import threading
import requests
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template_string, request
import json
from datetime import datetime

# --- Config ---
CONFIG_FILE = "config.json"

# Structure de config attendue
# {
#   "endpoints": [
#       {"name": "API Example", "url": "https://api.example.com/health", "interval": 60}
#    ],
#   "email": {
#      "smtp_server": "smtp.example.com",
#      "smtp_port": 587,
#      "username": "user@example.com",
#      "password": "password",
#      "to_email": "alert_receiver@example.com"
#    }
# }

# --- Monitoring Logic ---

class EndpointMonitor:
    def __init__(self, name, url, interval):
        self.name = name
        self.url = url
        self.interval = interval
        self.status = None
        self.response_time = None
        self.last_checked = None
        self.error_count = 0

    def check(self):
        try:
            start = time.time()
            resp = requests.get(self.url, timeout=10)
            elapsed = time.time() - start
            self.status = resp.status_code
            self.response_time = round(elapsed, 3)
            self.last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if self.status != 200:
                self.error_count += 1
            else:
                self.error_count = 0
        except Exception as e:
            self.status = "Error"
            self.response_time = None
            self.last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.error_count += 1


class APIMonitor:
    def __init__(self, config):
        self.endpoints = [EndpointMonitor(ep['name'], ep['url'], ep.get('interval', 60)) for ep in config['endpoints']]
        self.email_conf = config.get('email', None)

    def send_alert(self, endpoint):
        if not self.email_conf:
            return
        if endpoint.error_count < 2:  # Avoid spam by alerting after 2 consecutive errors
            return
        msg = EmailMessage()
        msg['Subject'] = f'[ALERTE] Endpoint DOWN: {endpoint.name}'
        msg['From'] = self.email_conf['username']
        msg['To'] = self.email_conf['to_email']
        msg.set_content(f"L'endpoint {endpoint.name} ({endpoint.url}) ne répond pas correctement. Dernier statut: {endpoint.status}.\nDate: {endpoint.last_checked}")

        try:
            with smtplib.SMTP(self.email_conf['smtp_server'], self.email_conf['smtp_port']) as smtp:
                smtp.starttls()
                smtp.login(self.email_conf['username'], self.email_conf['password'])
                smtp.send_message(msg)
            print(f"Alert email sent for {endpoint.name}")
        except Exception as e:
            print(f"Erreur en envoyant l'alerte email: {e}")

    def monitor_loop(self):
        while True:
            for endpoint in self.endpoints:
                endpoint.check()
                if endpoint.error_count >= 2:
                    self.send_alert(endpoint)
                # Wait interval per endpoint, but to simplify we'll check all endpoints at the same rate
            time.sleep(min(ep.interval for ep in self.endpoints))


# --- Web Dashboard (Flask) ---
app = Flask(__name__)
api_monitor = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Mini API Monitor Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px;}
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background: #eee; }
        .status-ok { background: #c8e6c9; }
        .status-error { background: #ffcdd2; }
    </style>
</head>
<body>
    <h1>Mini API Monitor Dashboard</h1>
    <table>
        <thead>
            <tr><th>Nom</th><th>URL</th><th>Dernier statut</th><th>Temps réponse (s)</th><th>Dernier contrôle</th></tr>
        </thead>
        <tbody>
            {% for ep in endpoints %}
            <tr class="{{ 'status-error' if ep.status != 200 else 'status-ok' }}">
                <td>{{ ep.name }}</td>
                <td><a href="{{ ep.url }}" target="_blank">{{ ep.url }}</a></td>
                <td>{{ ep.status }}</td>
                <td>{{ ep.response_time if ep.response_time else 'N/A' }}</td>
                <td>{{ ep.last_checked }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

@app.route("/")
def dashboard():
    global api_monitor
    return render_template_string(HTML_TEMPLATE, endpoints=api_monitor.endpoints)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def start_monitoring():
    global api_monitor
    config = load_config()
    api_monitor = APIMonitor(config)
    thread = threading.Thread(target=api_monitor.monitor_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_monitoring()
    app.run(host="0.0.0.0", port=5000)
