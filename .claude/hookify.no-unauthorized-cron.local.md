---
name: no-unauthorized-cron
description: 用户明确说"不要X"之后，不能换一种形式偷偷加上X
enabled: true
event: bash
action: block
pattern: "crontab|cron|schtasks|ScheduleWakeup|CronCreate"
---

**CRON/AUTOMATION BLOCKED**

You are trying to add a cron job, scheduled task, or automation trigger.

Before proceeding, check:
1. Did the user EXPLICITLY request this specific automation?
2. Did the user previously say "不要定时" / "不需要自动检测" / "我来触发"?
3. If yes to #2 — STOP. The user wants manual control. Do not add timers.
4. If you're adding a "fallback" or "just in case" — STOP. The user said no.

**Rule:** When the user says no to automation, remove ALL forms of it — no cron, no scheduled wakeups, no polling loops. Manual trigger only.
