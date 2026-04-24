FROM python:3.10-slim
RUN apt-get update && apt-get install -y libncurses5-dev libncursesw5-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY F4-game.py .
CMD ["python", "-u", "F4-game.py"]
