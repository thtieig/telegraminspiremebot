#!/usr/bin/env python3
import os
import json
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
import openai
import telegram # python-telegram-bot
import asyncio # Added for running async code

# --- Configuration ---
# Use the directory where the script is located
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR / ".env"
CONFIG_FILE = SCRIPT_DIR / "config.json"
LOG_FILE = SCRIPT_DIR / "bot.log"

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout) # Also print logs to console
    ]
)

# --- Load Environment Variables (Secrets) ---
try:
    load_dotenv(dotenv_path=ENV_FILE)
    # IONOS uses OpenAI compatible API, so the key variable name is the same
    # If IONOS gives you a different env variable name, change "OPENAI_API_KEY" here
    API_KEY = os.getenv("OPENAI_API_KEY")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in .env file.")
    if not API_KEY:
        # Check if IONOS requires a different key name maybe?
        # For now, assuming standard OPENAI_API_KEY usage
        raise ValueError("API_KEY (e.g., OPENAI_API_KEY) not found in .env file.")

    logging.info("Environment variables loaded successfully.")
except Exception as e:
    logging.error(f"Fatal Error loading environment variables: {e}")
    sys.exit(1) # Exit if secrets can't be loaded

# --- Load Configuration (Strict) ---
config = {}
try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    logging.info("Configuration file found and parsed.")

    # Define required keys
    required_keys = [
        "whitelisted_chat_ids",
        "openai_base_url",
        "openai_model",
        "openai_prompt"
    ]
    missing_keys = [key for key in required_keys if key not in config]
    empty_values = [key for key in required_keys if key in config and not config[key]] # Check for empty strings/lists

    if missing_keys:
        raise ValueError(f"Missing required keys in config.json: {', '.join(missing_keys)}")
    if empty_values:
        # We allow empty whitelisted_chat_ids list, but warn later. Check others.
        strict_empty_check = [key for key in empty_values if key != "whitelisted_chat_ids"]
        if strict_empty_check:
             raise ValueError(f"Required keys in config.json have empty values: {', '.join(strict_empty_check)}")

    # Check if whitelisted_chat_ids is a list
    if not isinstance(config["whitelisted_chat_ids"], list):
        raise ValueError("Config Error: 'whitelisted_chat_ids' must be a list (e.g., [12345])")

    # Assign validated config values to variables
    WHITELISTED_CHAT_IDS = config["whitelisted_chat_ids"]
    OPENAI_BASE_URL = config["openai_base_url"]
    OPENAI_MODEL = config["openai_model"]
    OPENAI_PROMPT = config["openai_prompt"]

    logging.info("Configuration loaded and validated successfully.")
    if not WHITELISTED_CHAT_IDS:
         logging.warning("Config Warning: 'whitelisted_chat_ids' is empty. No messages will be sent.")

except FileNotFoundError:
    logging.error(f"Fatal Error: config.json not found at {CONFIG_FILE}")
    sys.exit(1)
except json.JSONDecodeError:
    logging.error(f"Fatal Error: Could not decode config.json. Check its format.")
    sys.exit(1)
except ValueError as e:
    logging.error(f"Fatal Configuration Error: {e}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Fatal Error loading configuration: {e}")
    sys.exit(1)


# --- OpenAI/IONOS Function ---
def get_inspiring_message(api_key, base_url, model, prompt):
    """Gets an inspiring message from the configured OpenAI-compatible API."""
    logging.info(f"Requesting inspiring message from API endpoint: {base_url} using model: {model}")
    try:
        # Initialise client with IONOS base_url
        client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant creating inspiring messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8, # Adjust for more/less predictable text
            max_tokens=150 # Limit response length slightly more
        )
        message = response.choices[0].message.content.strip()
        logging.info("Successfully received message from API.")
        return message
    # Catch specific OpenAI errors, which should still apply to compatible APIs
    except openai.AuthenticationError:
         logging.error("API Authentication Error: Check your API Key in the .env file.")
         return None
    except openai.RateLimitError:
         logging.error("API Rate Limit Error: You might be exceeding your quota or limits.")
         return None
    except openai.NotFoundError:
         logging.error(f"API NotFound Error: The model '{model}' might not exist at '{base_url}'. Check config.json.")
         return None
    except openai.APIConnectionError:
         logging.error(f"API Connection Error: Could not connect to '{base_url}'. Check network or URL.")
         return None
    except Exception as e:
        logging.error(f"Error getting message from API: {e}")
        return None

# --- Telegram Function ---
async def send_telegram_message(bot_token, chat_ids, message):
    """Sends a message to specified Telegram chat IDs."""
    if not message:
        logging.warning("No message generated, skipping Telegram send.")
        return

    if not chat_ids:
        logging.warning("No target chat IDs configured or list is empty, skipping Telegram send.")
        return

    logging.info(f"Initialising Telegram Bot to send message...")
    bot = telegram.Bot(token=bot_token)
    sent_count = 0
    try:
        async with bot: # Ensure proper connection handling
            for chat_id in chat_ids:
                try:
                    logging.info(f"Attempting to send message to chat ID: {chat_id}")
                    await bot.send_message(chat_id=chat_id, text=message)
                    sent_count += 1
                    logging.info(f"Successfully sent message to chat ID: {chat_id}")
                    await asyncio.sleep(0.1) # Small delay between messages if sending to many
                except telegram.error.BadRequest as e:
                    logging.error(f"Telegram BadRequest Error for chat_id {chat_id}: {e}. Is the ID correct? Has the user started the bot?")
                except telegram.error.Forbidden as e:
                    logging.error(f"Telegram Forbidden Error for chat_id {chat_id}: {e}. Has the user blocked the bot?")
                except Exception as e:
                    logging.error(f"Error sending message to chat ID {chat_id}: {e}")
        logging.info(f"Finished sending messages. Attempted: {len(chat_ids)}, Succeeded: {sent_count}.")

    except Exception as e:
        logging.error(f"Failed to initialise or use Telegram Bot: {e}")

# --- Main Execution ---
async def main():
    logging.info("----- Inspiring Bot Script Started -----")
    # 1. Get message from API (OpenAI/IONOS)
    inspiring_message = get_inspiring_message(
        api_key=API_KEY,
        base_url=OPENAI_BASE_URL,
        model=OPENAI_MODEL,
        prompt=OPENAI_PROMPT
    )

    # 2. Send message via Telegram if successful
    if inspiring_message:
        await send_telegram_message(TELEGRAM_TOKEN, WHITELISTED_CHAT_IDS, inspiring_message)
    else:
        logging.error("Failed to get inspiring message. Cannot send via Telegram.")

    logging.info("----- Inspiring Bot Script Finished -----")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
