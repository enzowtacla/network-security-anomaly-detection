import json
import ssl
import time
import urllib.request
import urllib.parse
from pathlib import Path
from base64 import b64encode
from datetime import datetime, timedelta, timezone

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
STATE_FILE = BASE_DIR / ".telegram_alert_state.json"


def load_config():
    config = {}

    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        key, separator, value = line.partition("=")

        if separator:
            config[key.strip()] = value.strip().strip('"').strip("'")

    return config


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())

    return {"processed_ids": []}


def save_state(state):
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2))
    temporary.replace(STATE_FILE)


def search_alerts(config):
    url = config["ELASTICSEARCH_URL"].rstrip("/")
    credentials = (
        f'{config["ELASTICSEARCH_USERNAME"]}:'
        f'{config["ELASTICSEARCH_PASSWORD"]}'
    )

    encoded = b64encode(credentials.encode()).decode()

    context = ssl.create_default_context(
        cafile=config["ELASTICSEARCH_CA_CERT"]
    )

    start_time = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()

    query = {
        "size": 100,
        "sort": [
            {"@timestamp": {"order": "asc"}}
        ],
        "query": {
            "bool": {
                "filter": [
                    {"exists": {"field": "snort.rule_id"}},
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time
                            }
                        }
                    }
                ]
            }
        }
    }

    request = urllib.request.Request(
        f"{url}/filebeat-*/_search",
        data=json.dumps(query).encode(),
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        context=context,
        timeout=15
    ) as response:
        result = json.load(response)

    return result["hits"]["hits"]


def send_telegram(config, message):
    url = (
        "https://api.telegram.org/bot"
        f'{config["TELEGRAM_BOT_TOKEN"]}/sendMessage'
    )

    data = urllib.parse.urlencode({
        "chat_id": config["TELEGRAM_CHAT_ID"],
        "text": message
    }).encode()

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.load(response)

    if not result.get("ok"):
        raise RuntimeError("Telegram rejected the message")


def format_alert(hit):
    source = hit["_source"]
    snort = source.get("snort", {})

    return (
        "LAB 5 - SECURITY ALERT\n\n"
        f'Time: {source.get("@timestamp", "Unknown")}\n'
        f'Alert: {snort.get("alert_type", "Unknown")}\n'
        f'Rule: {snort.get("rule_id", "Unknown")}\n'
        f'Source: {snort.get("source_ip", "Unknown")}\n'
        f'Destination: {snort.get("destination_ip", "Unknown")}'
    )

def main():
    config = load_config()
    state = load_state()

    processed = set(state["processed_ids"])

    print("Checking Elasticsearch for Snort alerts...")

    alerts = search_alerts(config)
    groups = {}

    for alert in alerts:
        event_id = f'{alert["_index"]}:{alert["_id"]}'

        if event_id in processed:
            continue

        source = alert["_source"]
        snort = source.get("snort", {})

        key = (
            snort.get("rule_id", "Unknown"),
            snort.get("source_ip", "Unknown"),
            snort.get("destination_ip", "Unknown")
        )

        groups.setdefault(key, []).append((event_id, alert))

    notifications = 0

    for events in groups.values():
        first_alert = events[0][1]
        message = format_alert(first_alert)

        message += f"\n\nEvents detected: {len(events)}"

        send_telegram(config, message)

        for event_id, _ in events:
            processed.add(event_id)

        state["processed_ids"] = list(processed)[-1000:]
        save_state(state)

        notifications += 1
        time.sleep(0.2)

    print(f"Notifications sent: {notifications}")

if __name__ == "__main__":
    main()
