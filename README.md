F4: Console Tower Defense
A console-based Tower Defense game written in Python using the curses library. The project is fully containerized for easy deployment.

Getting Started
1. Cloning the repository
git clone https://github.com/sudo-pacman-Syy/F1.git
cd F1
2. Running the game via Docker
We use Docker to ensure the game runs in an isolated environment, eliminating the need to install dependencies directly on your system.
Make sure you have Docker and Docker Compose installed.

make run
This command will automatically build the image and launch the game in interactive mode.
To stop the container, use:

make clean
3. Running without Docker (Locally)
If you prefer to run the game directly in your Python environment:

pip install -r requirements.txt

python F4-game.py
(Note: On Windows, ensure that windows-curses is installed from the requirements file.)
