# THE WEDNESDAY GLOBE — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Yami-euy/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Yami-euy/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Sum up the world's news of Wednesday 25 November 2026 in one image.

## The entry

`entry.png` is a one-page broadsheet — **THE WEDNESDAY GLOBE** — with 50
verified stories: 3 illustrated lead cards (Hormuz tankers hit by mines,
Ukraine's strikes on two Rosneft refineries, Gaza), 10 small illustrated
cards, a big-number stat strip, a UTC timeline, a numbered world map, an
IN BRIEF list of 37 more stories, region counts, how-sure badges
(OFFICIAL / CONFIRMED / REPORTED / CLAIM), and a DATE CHECK footer.
Market stats use Tuesday close + Wednesday pre-market. The US Wednesday
session had not closed at research time, so no Wednesday close is claimed;
tonight's Champions League fixtures are listed without scores.

## How it works

- `render.py` (local only, needs Pillow) renders `entry.png` (1024×1024).
- `main.py` is a standard-library-only copier: it copies the pre-rendered
  `entry.png` from this repository to `/output/entry.png`, byte for byte.
  The grader runs standard library only, so the program imports nothing
  beyond `os`, `shutil`, `sys` and `pathlib`.
- `stories.py` holds the story data used by the renderer.

## Bounty

[Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125)
