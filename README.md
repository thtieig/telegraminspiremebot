# Inspiring Telegram Bot

## Overview

This project runs a Python script on a server to send a daily inspirational or mindful message via a Telegram bot. It uses an OpenAI-compatible API (like the one provided by IONOS or OpenAI itself) to generate unique messages each day based on a configurable prompt. Messages are sent only to whitelisted Telegram users. The script is designed to be run automatically using `cron`.

## Features

*   Fetches daily unique messages from an OpenAI-compatible API.
*   Sends messages via a dedicated Telegram Bot.
*   Whitelists specific Telegram Chat IDs to receive messages.
*   Uses a `.env` file for secure storage of API keys and tokens.
*   Uses a `config.json` file for easy configuration of prompts, API endpoints, and target users.
*   Scheduled execution using `cron`.
*   Logs script activity to `bot.log` and cron output to `cron.log`.
*   Uses a dedicated Python virtual environment.

## Prerequisites

*   A Linux server (tested on Debian 12).
*   `python3`, `python3-pip`, `python3-venv` installed (`sudo apt install python3 python3-pip python3-venv`).
*   `git` installed (`sudo apt install git`).
*   A Telegram account.
*   Access credentials for an OpenAI-compatible API:
    *   API Key (e.g., your OpenAI key or IONOS key)
    *   API Base URL (e.g., `https://api.openai.com/v1` or `https://openai.inference.de-txl.ionos.com/v1`)
*   A Telegram Bot Token.

## Setup Instructions

Follow these steps on your Linux server:

1.  **Clone the Repository:**
    ```bash
    git clone https://thtieig@bitbucket.org/thtieig/telegraminspiremebot.git
    cd telegraminspiremebot
    ```
    *(Replace `<your-bitbucket-repo-url.git>` with the actual URL of your repository)*

2.  **Create Python Virtual Environment:**
    ```bash
    python3 -m venv inspiringbot
    ```

3.  **Activate Virtual Environment:**
    ```bash
    source inspiringbot/bin/activate
    ```
    *(Your command prompt should now start with `(inspiringbot)`)*

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

You need to configure secrets and settings before running the script.

**1. Telegram Bot Setup:**

*   **Create the Bot & Get Token:**
    *   Open Telegram and search for `BotFather`.
    *   Start a chat (`/start`).
    *   Type `/newbot` and follow the instructions to name your bot and choose a username (must end in `bot`).
    *   `BotFather` will give you an **HTTP API token**. **Copy this token carefully.** This is your `TELEGRAM_BOT_TOKEN`.
*   **Get Your Chat ID:**
    *   Search for the bot `@userinfobot` in Telegram.
    *   Start a chat (`/start`).
    *   It will reply with your **Chat ID** (a number). Copy this ID. You can get IDs for other users you want to whitelist this way too (they need to message `@userinfobot`).
*   **IMPORTANT: Start Your Bot:**
    *   Search for *your new bot's username* in Telegram.
    *   Open the chat with your bot and tap **'Start'** or type `/start`.
    *   **Your bot cannot send you messages unless you do this first!**

**2. API Credentials:**

*   Make sure you have your **API Key** and the correct **API Base URL** from your provider (OpenAI, IONOS, etc.).

**3. Create `.env` File (Secrets):**

*   Create a file named `.env` in the `inspiring_bot` directory:
    ```bash
    nano .env
    ```
*   Add your secrets, replacing the placeholders:
    ```dotenv
    # Telegram Bot Token from BotFather
    TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

    # Your API Key (from OpenAI, IONOS, etc.)
    OPENAI_API_KEY=YOUR_API_KEY_HERE
    ```
*   Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).
*   **Security:** This file contains secrets and is listed in `.gitignore`. **Never commit `.env` to your repository.** Set restrictive permissions: `chmod 600 .env`.

**4. Configure `config.json` (Settings):**

*   Rename `config.json.example` to `config.json` and edit it:
    ```bash
    nano config.json
    ```
*   Modify the contents to match your requirements:
    ```json
    {
      "whitelisted_chat_ids": [
        123456789,  # Replace with YOUR Chat ID. Add more IDs separated by commas.
        987654321   # Example: Add another Chat ID here
      ],
      "openai_base_url": "https://openai.inference.de-txl.ionos.com/v1", # Replace with your API provider's URL
      "openai_model": "meta-llama/Llama-3.3-70B-Instruct", # Replace with the model you want to use
      "openai_prompt": "Generate a short (2-3 sentences), uplifting and inspiring message for starting the day. Focus on mindfulness, positivity, or the beauty of life. Make it thoughtful and unique each time. Do not include greetings like 'Good morning'."
    }
    ```
    *   `whitelisted_chat_ids`: A list of numeric Telegram Chat IDs that should receive the message. **Ensure users have `/start`ed your bot!**
    *   `openai_base_url`: The base URL for your API provider.
    *   `openai_model`: The specific model identifier for the API.
    *   `openai_prompt`: The instruction given to the AI to generate the message. Customise this as you like! Here some examples:
        * EXAMPLE 1: "Compose a short, uplifting sentence in British English that inspires self love, gratitude, and positivity for the day ahead. Ensure the message is unique, thoughtful, and does not include greetings like 'Good morning'."
        * EXAMPLE 2: "Generate a concise and motivational sentence in British English centred on self love and positive energy. The message should be unique and encourage a mindset of gratitude and self care, without any standard greetings."
        * EXAMPLE 3: "Write a brief, inspirational sentence in British English that promotes self love, positivity, and gratitude. The message must be uniquely crafted each time and avoid any conventional greetings."

*   Save and exit (`Ctrl+O`, Enter, `Ctrl+X`).

## Running the Script Manually (Testing)

1.  Ensure your virtual environment is active:
    ```bash
    cd ~/inspiring_bot  # Or your project directory
    source inspiringbot/bin/activate
    ```
2.  Run the script directly:
    ```bash
    python send_message.py
    ```
3.  Check the output in your terminal for any errors.
4.  Check the log file: `cat bot.log`
5.  Check your Telegram account (if your Chat ID is whitelisted) for the message.

## Scheduling Daily Messages (Cron)

To send the message automatically every morning:

1.  **Find Absolute Paths:** You need the full paths to your Python interpreter (within the venv) and your script.
    *   Find Python path (while venv is active): `which python` (e.g., `/home/your_user/inspiring_bot/inspiringbot/bin/python`)
    *   Find script path: `pwd` (while in `~/inspiring_bot`) will give you the directory (e.g., `/home/your_user/inspiring_bot`). The script path is then `/home/your_user/inspiring_bot/send_message.py`.

2.  **Edit Crontab:**
    ```bash
    crontab -e
    ```
    *(Choose an editor like `nano` if prompted)*

3.  **Add Cron Job:** Add a line like the following at the bottom, **replacing the placeholder paths** with the absolute paths you found above. This example runs at 8:00 AM daily:
    ```crontab
    # Send daily inspiring message at 8:00 AM
    0 8 * * * /home/your_user/inspiring_bot/inspiringbot/bin/python /home/your_user/inspiring_bot/send_message.py >> /home/your_user/inspiring_bot/cron.log 2>&1
    ```
    *   `0 8 * * *`: Minute 0, Hour 8 (8 AM), Every Day, Every Month, Every Day of the week. Change `8` to your desired hour (0-23).
    *   `/home/your_user/.../python`: **Use your absolute path to python.**
    *   `/home/your_user/.../send_message.py`: **Use your absolute path to the script.**
    *   `>> /home/.../cron.log 2>&1`: Appends all output (standard and error) to `cron.log` in your project directory for debugging.

4.  **Save and Exit:** (`Ctrl+O`, Enter, `Ctrl+X` for nano). The cron job is now active.

5.  **Automatic Restart:** The `cron` service on Debian 12 typically starts automatically on system boot, so your scheduled job should persist after reboots. You can check its status with `systemctl status cron`.

## File Structure

```
inspiring_bot/
├── inspiringbot/      (Python virtual env - ignored by git)
├── .env              (Secrets - **ignored by git**)
├── .gitignore        (Specifies files for git to ignore)
├── config.json       (User configuration)
├── requirements.txt  (Python dependencies)
├── send_message.py   (The main Python script)
├── bot.log           (Logs from send_message.py - ignored by git)
└── cron.log          (Logs from cron execution - ignored by git)
```

---
Enjoy your daily dose of inspiration!
```

**How to Use:**

1.  Navigate to your project directory on the server: `cd ~/inspiring_bot`
2.  Create the file: `nano README.md`
3.  Paste the entire content above into the `nano` editor.
4.  Save and exit: `Ctrl+O`, Enter, `Ctrl+X`.
5.  Add the new file to Git: `git add README.md`
6.  Commit the change: `git commit -m "Add README.md"`
7.  Push to Bitbucket: `git push origin main` (or `master`, depending on your branch name).

