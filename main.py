import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LIST_URL = "https://khlongluang.go.th/public/list/data/index/menu/1554"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
SEEN_FILE = os.getenv("SEEN_FILE", "seen_ids.json")
NOTICES_FILE = os.getenv("NOTICES_FILE", "water_notices.jsonl")  # append-only log
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

WATER_OUTAGE_KEYWORDS = [
    "ปิดน้ำ", "งดจ่ายน้ำ", "หยุดจ่ายน้ำ",
    "งดจ่ายน้ำชั่วคราว", "หยุดจ่ายน้ำชั่วคราว",
    "สำรองน้ำ", "ประกาศสำรองน้ำ",
    "ซ่อมท่อประปา", "ซ่อมท่อแตก", "ท่อประปาแตก",
    "น้ำประปาไม่ไหล", "ปรับปรุงระบบประปา"
]


def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_seen_ids(ids):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False)


def append_notice(notice):
    with open(NOTICES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(notice, ensure_ascii=False) + "\n")


def fetch_list():
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    posts = []
    for row in soup.select("div.row.data-row"):
        img = row.select_one("a.divimages img")
        link = row.select_one("a.listdataconfig_link")
        if not img or not link:
            continue
        href = str(link.get("href", ""))
        match = re.search(r"/id/(\d+)/", href)
        if not match:
            continue
        post_id = match.group(1)
        title = str(img.get("alt", "")).strip()
        full_url = f"https://khlongluang.go.th{href}" if href.startswith("/") else href
        posts.append({"id": post_id, "title": title, "url": full_url})
    return posts


def is_water_outage(text):
    return any(kw in text for kw in WATER_OUTAGE_KEYWORDS)


def send_discord_notification(notice):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = {
        "embeds": [
            {
                "title": "ประกาศน้ำประปา",
                "description": notice["title"],
                "url": notice["url"],
                "color": 0xE67E22,  # orange
                "fields": [
                    {"name": "ลิงก์", "value": notice["url"], "inline": False},
                ],
                "footer": {"text": "คลองหลวง อปท. • อัตโนมัติ"},
                "timestamp": notice["fetched_at"],
            }
        ]
    }
    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[discord] failed to send notification: {e}")


def run():
    seen = load_seen_ids()
    posts = fetch_list()

    new_notices = []
    for post in posts:
        if post["id"] in seen:
            continue
        seen.add(post["id"])

        if is_water_outage(post["title"]):
            notice = {**post, "fetched_at": datetime.now().isoformat()}
            append_notice(notice)
            send_discord_notification(notice)
            new_notices.append(notice)

    save_seen_ids(seen)
    return new_notices


if __name__ == "__main__":
    notices = run()
    for n in notices:
        print(f"{n['title']}\n{n['url']}\n")