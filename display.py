import json

NOTICES_FILE = "water_notices.jsonl"

def load_notices():
    notices = []
    with open(NOTICES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                notices.append(json.loads(line))
    return notices

def display(notices, limit=10):
    notices = sorted(notices, key=lambda n: n["fetched_at"], reverse=True)
    for n in notices[:limit]:
        print(f"[{n['fetched_at'][:16]}] {n['title']}")
        print(f"  → {n['url']}\n")

if __name__ == "__main__":
    notices = load_notices()
    print(f"ทั้งหมด {len(notices)} ประกาศ\n")
    display(notices)