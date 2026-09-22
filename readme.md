# Sysadmin Telegram Bot 🐧🔧

A Telegram bot powered by a local LLM (Ollama), roleplaying as a tired system administrator on a long night shift. The bot remembers conversation context and runs in an isolated Docker environment with GPU acceleration support for faster inference.

## Features

* **Local LLM**: Inference runs locally via the Ollama container (uses the `gemma2:9b` model with a custom system prompt).

* **Context Memory**: The bot remembers the last 15 messages in each chat to maintain a meaningful dialogue.

* **Group Chat Support**: In group chats, it only reacts to direct mentions (@username) or replies to its messages. This prevents spam and keeps the context relevant.

* **GPU Acceleration**: Out-of-the-box support for Nvidia GPUs for fast response generation.

## Prerequisites

* Docker

* Docker Compose

* [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html?utm_source=gemini) (for hardware acceleration)

## Installation and Setup

1. Clone the repository:

   ```
   git clone https://github.com/NePalladin/ollama-tg-sysadmin.git
   cd ollama-tg-sysadmin
   
   ```

2. Create a `.env` file in the root directory and add your Telegram bot token (you can get one from [@BotFather](https://t.me/BotFather?utm_source=gemini)):

   ```
   TELEGRAM_TOKEN=your_token_here
   
   ```

3. Build and run the containers in the background:

   ```
   docker compose up -d --build
   
   ```

4. On the first run, you need to build the custom `sysadmin` model inside the Ollama container using the provided `Modelfile`. Execute the following commands:

   ```
   # Copy the Modelfile into the container
   docker cp Modelfile ollama:/Modelfile
   
   # Create the model
   docker exec -it ollama ollama create sysadmin -f /Modelfile
   
   ```

## Project Structure

* `compose.yaml` — Docker services configuration (Ollama + Python container for the bot).

* `Dockerfile` — Instructions to build the bot image based on `python:3.11-alpine`.

* `main.py` — The core logic for handling the Telegram API (via pyTelegramBotAPI) and communicating with the Ollama API.

* `Modelfile` — Instructions for Ollama, setting the base model (`gemma2:9b`) and the strict system prompt (persona) of the bot.

* `requirements.txt` — Python dependencies.
