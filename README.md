# Matrix Hunter Universe

> **4 mini-games powered by Linear Algebra (Matrix) mechanics**

---

## 🎮 Games

| Game | Type | Matrix Mechanic |
|------|------|-----------------|
| **Matrix Sniper** | Top-down shooter | Rotation matrix curves bullets; reflection matrix for ricochet bullets; scale matrix for scope zoom |
| **Matrix Assassin** | Stealth infiltration | Reflection matrix mirrors guard patrol routes; rotation matrix sweeps vision cones |
| **Matrix Space Battle** | 2D space shooter | Grid/V formations via rotation-transformed point arrays; scale-pulse power-ups; rotation matrix for boss bullet fans |
| **Matrix Runner** | Endless runner | Shear matrix speed-warp; translation matrix parallax layers; rotation matrix limb animation; scale matrix for magnet |

---

## ▶ Desktop (Quick Start)

### Requirements
```
1. **Python 3.10+**
2. **Pygame-CE (Community Edition)**
```

### Installation & Run
```bash
pip install pygame-ce
python main.py
```

> The game generates all sounds procedurally — **no external audio files needed**.

---

## 📱 Mobile (Android)

The game can be packaged as an Android APK using **Buildozer** (Linux / WSL required).

### 1 — Install Buildozer
```bash
pip install buildozer
```

### 2 — Install Android dependencies (Ubuntu / WSL)
```bash
sudo apt install -y git unzip wget \
    libncurses5:i386 libstdc++6:i386 zlib1g:i386 \
    openjdk-17-jdk
```

### 3 — Build the APK
```bash
cd MatrixHunterUniverse
buildozer android debug
```

The APK will be at `bin/MatrixHunterUniverse-1.0.0-debug.apk`.

### 4 — Deploy to device
```bash
buildozer android deploy run logcat
```

> **Note:** First build downloads the Android SDK/NDK automatically (~3 GB).
> Mobile uses the integrated `touch_controls.py` for on-screen virtual joypads, buttons, and swipe gestures.

---

## 🗂 Project Structure

```
MatrixHunterUniverse/
├── main.py            # Entry point
├── game.py            # GameManager (state machine)
├── menu.py            # All screens (loading, main, select, pause, settings, scores)
├── settings.py        # Settings persistence
├── save_manager.py    # High-score & save-state JSON
├── sound_manager.py   # Procedural sound generation (numpy)
├── animation.py       # Particles, screen shake, matrix rain, starfield
├── ui.py              # HUD widgets (health bar, timer, FPS, buttons)
├── touch_controls.py  # Virtual controller logic & swipe gestures for mobile
├── config.py          # Constants, colours, enums
│
├── games/
│   ├── common.py      # Matrix math + shared base classes
│   ├── sniper.py      # Matrix Sniper
│   ├── assassin.py    # Matrix Assassin
│   ├── space_battle.py# Matrix Space Battle
│   └── runner.py      # Matrix Runner
│
├── data/              # Created at runtime (highscores.json, settings.json)
├── buildozer.spec     # Android packaging config
└── README.md
```

---

## ⌨ Controls

### Matrix Sniper
| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| Mouse | Aim |
| Left Click | Shoot |
| Q / E | Switch weapon |
| R | Reload |
| Z | Toggle scope |
| ESC | Pause |

### Matrix Assassin
| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| C / Left Ctrl | Hold to crouch |
| E | Interact (unlock door) / Stealth Kill |
| ESC | Pause |

### Matrix Space Battle
| Key | Action |
|-----|--------|
| WASD / Arrows | Steer + thrust |
| Space / Z | Fire |
| X | Drop bomb |
| ESC | Pause |

### Matrix Runner
| Key | Action |
|-----|--------|
| Space / Up / W | Jump (double-jump) |
| Ctrl / Down / S | Slide |
| ESC | Pause |

### Global
| Key | Action |
|-----|--------|
| F11 | Toggle fullscreen |

---

## 🔢 Linear Algebra Mechanics

```
Rotation Matrix  R(θ) = | cos θ  -sin θ |
                         | sin θ   cos θ |

Scale Matrix     S(s) = | sx   0 |
                         | 0   sy |

Reflection (Y)   Ry   = | -1   0 |
                         |  0   1 |

Shear            H    = |  1  shx |
                         | shy  1  |
```

Each game uses these transformations **as gameplay mechanics**, not as quiz questions.

---

## 🏆 High Scores
Stored in `data/highscores.json` — top 10 per game, persisted between sessions.

---

## 📄 License
MIT License — free to use, modify and distribute.
