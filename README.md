# PWA Water Outage Notifier -> Discord

Thai municipal water authority (PWA) announcements are usually buried in
government CMS pages or Facebook posts, easy to miss. This project polls
the Khlong Luang municipality announcement page on a schedule, filters for
water outage / supply interruption notices using Thai keyword matching,
deduplicates against previously seen posts, and pushes new alerts straight
to a Discord channel via webhook.

**Flow:** poll -> filter -> dedupe -> log (JSONL) -> notify (Discord)

## Why
Government and utility notices in Thailand are often scattered across
blogs, Facebook pages, and municipal CMS sites with no RSS or push
notification support. This tool turns one such source into a simple push
alert so you don't have to check manually.

## Stack
- Python (`requests`, `BeautifulSoup`)
- JSONL for append-only notice logging
- Discord webhook for push notifications
- Cron for scheduling

## Example
<img width="766" height="279" alt="image" src="https://github.com/user-attachments/assets/00311dd9-ac2a-4053-822b-605bee47266e" />
