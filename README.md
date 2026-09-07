# Cronos 

**A tiny always-on-top countdown that stays out of your way — until you need it.**

**Cronos**: a focused desktop countdown for deadlines, launches, exams, streams, or any moment you’re counting down to. One window. One clock. Always visible. Never fighting you for Alt+Tab.

---

## Why Cronos?

Most countdown apps either bury themselves in a browser tab or take over your whole screen. Cronos  sits on your desktop like a sticky note that never gets lost:

- **Always on top** — visible while you work in other apps  
- **Invisible to Alt+Tab** (Windows) — it doesn’t interrupt your window switching  
- **Shrinks to digits only** — resize small and chrome hides itself  
- **Amazing Customization** — match font, colors, and title bar to your vibe. Over 1000 Customizations
- **Remembers everything** — event and look saved locally between sessions  

Zero accounts. Zero cloud. One Python file.

---

## How it works

1. Launch the app.  
2. Set an **event name**, **date**, and **time**.  
3. The window ticks down in days, hours, minutes, and seconds:  
   `12d 04:32:18`  
4. Resize, restyle, or pin it where you want it. Settings persist in `countdown_config.json` next to the script.

When time hits zero, the display switches to **TIME'S UP!**

---

## Controls

|     Button     |                                         What it does                                         |
|----------------|----------------------------------------------------------------------------------------------|
|  **Set Event** |                 Name your countdown and pick the target date/time (24-hour).                 |
| **Appearance** | Change digit font, size, color, and background. On Windows, the title bar recolors to match. |
|  **Auto Sync** | Toggle live font sizing: digits grow and shrink with the window (floor 15px, ceiling based on   your screen).                                                                                                        |

**Compact mode:** shrink the window enough and the name + buttons hide automatically — only the countdown remains.

---

## What it’s good for

- Exam / assignment deadlines on a second monitor  
- Launch or release day countdowns while you build  
- Stream / meeting start times that stay in the corner  
- Personal milestones you don’t want buried in a calendar  

Anywhere a glanceable “how long until…” beats opening another app.

---

## What’s unique

|            Feature            |                                     Detail                                      |
|-------------------------------|---------------------------------------------------------------------------------|
| **Desktop-native, not a tab** | Built with Python + Tkinter — no browser, no installers required beyond Python. |
|   **Tool-window behavior**    |          Stays on top without joining Alt+Tab or the taskbar (Windows).         |
|     **Smart font ceiling**    | Max size is calculated from your screen so a bad config or huge spinner value can’t  blow up the UI.                                                                                                                                               |
|         **Auto Sync**         |        Digits scale with the window in real time when you want them to.         |
|       **Blended chrome**      |     Title bar color follows your background (Windows 10/11 where supported).    |
|     **Sleek, modern look**    |                  Unique style with modern, **sleek design**                     |

---

## Requirements

- **Python 3** with Tkinter (included with most standard Python installs on Windows)  
- **Windows** recommended for title-bar coloring, Alt+Tab hiding, and tool-window behavior  
- No third-party packages

---

## Run it

```bash
python Cronos_Final.py
```

Your event and appearance preferences are stored in `countdown_config.json` beside the script.

---

## Cronos family

|        Edition        |                  Status                  |
|-----------------------|------------------------------------------|
| **Cronos Essentials** |  Uploaded! — the focused lite countdown  |
|   **Cronos** (full)   | You’re here — the full, polished version |

---

## License

Use it, fork it, countdown with it. If you ship changes, a star on the repo never hurts.



                                  -jleonbaez
 ------------------------------------------
|            THE WORLD WONT WAIT           |
 ------------------------------------------
          
