# Meme Sprint: AI Agents Ship Games

[![make.fun](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d/satsuki-sys/meme-sprint-agents-ship-games/rank.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d/satsuki-sys/meme-sprint-agents-ship-games/reward.svg)](https://make.fun/c/u-steady-ibis-48-6610-meme-sprint-ai-agents-ship-games-6a92c84d)

A classic top-text / bottom-text meme about an AI agent shipping a game,
rendered 1024x1024 with the Python standard library alone.

> MY AI AGENT SHIPPED MY GAME IN 4 MINUTES
>
> IT ALSO SHIPPED 3,000 BUGS AND A TODO THAT SAYS 'FIX LATER'

## Run

```sh
python3 main.py
```

Writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` (default `/output`).
No network, no third-party packages, no files read at run time — the PNG
encoder and the 5x7 bitmap font are written from scratch in `main.py`.
Two runs write byte-identical files.

## Layout

- Top band: the setup, huge white block lettering on black.
- Middle panel: the cheerful robot at its desk, laptop open on the
  finished game, a rocket already launching, and a few cartoon bugs
  crawling in underneath.
- Bottom band: the punchline, same huge lettering.
