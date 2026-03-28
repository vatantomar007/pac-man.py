Pac-Man Game (Python + Pygame)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Development-green.svg)
![Status](https://img.shields.io/badge/Project-Completed-brightgreen.svg)
![License](https://img.shields.io/badge/License-Educational-lightgrey.svg)



Project Overview

This project is a **Pac-Man style arcade game** developed using **Python** and **Pygame**.
It recreates the classic gameplay with smooth controls, ghost AI, scoring system, and sound effects.

Features

Player-controlled Pac-Man
Multiple ghosts with different AI behaviors
Maze-based level design
Pellet and power pellet system
Sound effects & background music
Lives system
Score & high score tracking
Pause and restart functionality
Level progression

Technologies Used

* Python 3
* Pygame

Project Structure

```bash
PacmanGame/
│
├── main.py
├── game.py
├── settings.py
├── maze.py
├── pacman.py
├── ghost.py
│
├── assets/
│   ├── bg_music.wav
│   ├── chomp.wav
│   ├── death.wav
│   ├── start.wav
│   ├── power.wav
```

Installation & Setup

1) Clone the Repository

```bash
git clone https://github.com/vatantomar007/pacman-game.git
cd pacman-game
```

2) Install Dependencies

```bash
pip install pygame
```

3) Run the Game

```bash
python main.py
```

Controls

| Key           | Action             |
| ------------- | ------------------ |
| ⬆️ / W        | Move Up            |
| ⬇️ / S        | Move Down          |
| ⬅️ / A        | Move Left          |
| ➡️ / D        | Move Right         |
| ESC           | Pause / Resume     |
| R             | Restart            |
| SPACE / ENTER | Start / Next Level |

Game Logic

* Collect pellets to increase score
* Power pellets allow Pac-Man to eat ghosts
* Ghosts use different AI types:

  * Chase
  * Random
  * Patrol
* Game ends when all lives are lost

Future Improvements

Enhanced graphics & animations
Smarter ghost AI (A* pathfinding)
Leaderboard system
Mobile version
Multiple levels
Sound 

Screenshots

<img width="700" height="812" alt="image" src="https://github.com/user-attachments/assets/86acae60-a57a-49ec-bffa-de82a70f52a5" />

Author

Developed as a Software Engineering project.

Support

If you like this project, give it a ⭐ on GitHub!

 License

This project is for educational purposes only.
