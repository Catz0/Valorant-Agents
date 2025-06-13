from flask import Flask, render_template, request
import requests
from translations import translations

app = Flask(__name__)

BASE_URL = "https://valorant-api.com/v1/agents"


def fetch_agent(lang):
    url = f"{BASE_URL}?isPlayableCharacter=true&language={lang}"
    res = requests.get(url)
    print("API response status:", res.status_code)
    print("Returned JSON:", res.json())  # <-- TEMP: for debugging
    return res.json().get('data', []) if res.status_code == 200 else []
    # url = f"{BASE_URL}?isPlayableCharacter=true&language={lang}"
    # res = requests.get(url)
    # return res.json().get('data', []) if res.status_code == 200 else []

@app.route('/')
def index():
    lang_options = {
        'en-US': 'English (US)',
        'es-ES': 'Spanish (Spain)',
        'pt-BR': 'Portuguese (Brazil)',
        'fr-FR': 'French',
        'de-DE': 'German',
        'ja-JP': 'Japanese',
        'ko-KR': 'Korean',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ru-RU': 'Russian'
    }

    lang = request.args.get("lang", "en-US")
    role = request.args.get("role", "").lower()
    search = request.args.get("search", "").lower()

    agents = fetch_agent(lang)

    data = translations.get(lang, translations["en-US"])
    ui_labels = data["ui"]
    roles_translated = data["roles"]

    print(f"Role filter from URL: '{role}'")
    for a in agents:
        role_name = a.get("role", {}).get("name", "").lower()
        print(f"Agent: {a['displayName']}, role.name: '{role_name}'")

    if role:
        translated_role_name = roles_translated.get(role, role).lower()
        agents = [
            a for a in agents
            if a.get("role") and a["role"].get("displayName", "").lower() == translated_role_name
        ]

    if search:
        agents = [a for a in agents if search in a["displayName"].lower()]

    return render_template(
        "index.html",
        agents=agents,
        current_lang=lang,
        current_role=role,
        search=search,
        labels=ui_labels,
        role_names=roles_translated,
        lang_options=ui_labels["languages"],
    )

@app.route('/agent/<uuid>')
def agent_detail(uuid):
    lang = request.args.get("lang", "en-US")
    labels = translations.get(lang, translations["en-US"])

    try:
        res = requests.get(f"{BASE_URL}/{uuid}?language={lang}")
        res.raise_for_status()
        agent = res.json().get("data")
        if not agent:
            return render_template("error.html", message="agent not found.", labels=labels, current_lang=lang)
    except requests.exceptions.RequestException as e:
        return render_template("error.html", message=f"API error: {e}", labels=labels, current_lang=lang)

    return render_template("agent.html", agent=agent, current_lang=lang, labels=labels["ui"])

if __name__ == "__main__":
    app.run(debug=True)
