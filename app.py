from flask import Flask, render_template, request
import requests

app = Flask(__name__)

BASE_URL = "https://valorant-api.com/v1/agents"

@app.route('/')
def index():
    lang = request.args.get("lang", "en-US")
    role = request.args.get("role", "")
    search = request.args.get("search", "").lower()

    res = requests.get(f"{BASE_URL}?isPlayableCharacter=true&language={lang}")
    agents = res.json()["data"] if res.status_code == 200 else []

    # Filter agents by role
    if role:
        agents = [a for a in agents if a["role"] and a["role"]["displayName"].lower() == role.lower()]
    # Filter agents by search query
    if search:
        agents = [a for a in agents if search in a["displayName"].lower()]

    return render_template("index.html", agents=agents, current_lang=lang, current_role=role, search=search)

@app.route('/agent/<uuid>')
def agent_detail(uuid):
    lang = request.args.get("lang", "en-US")
    res = requests.get(f"{BASE_URL}/{uuid}?language={lang}")
    agent = res.json()["data"] if res.status_code == 200 else None
    return render_template("agent.html", agent=agent, current_lang=lang)

if __name__ == "__main__":
    app.run(debug=True)