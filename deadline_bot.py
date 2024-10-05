import os
import urllib3
import json
import logging


from urllib3.exceptions import HTTPError, MaxRetryError, NewConnectionError
from datetime import datetime, date, time
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import filters, ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler
from dotenv import load_dotenv
from typing import Union, Dict, Any, cast

from PersonalFilters import PersonalFilters


# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set the minimum log level to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.StreamHandler()  # Output logs to the console
    ]
)

# Create a logger instance
logger = logging.getLogger(__name__)
# Load environment variables
load_dotenv()

# Get the bot token and chat ID from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TOKEN or not CHAT_ID:
    logger.error("Please set the TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
    exit(1)

# Set the deadline date (format: YYYY-MM-DD)
DEADLINE = datetime.strptime(os.getenv('DEADLINE_DATE'), '%Y-%m-%d').date()

GITHUB_URL = os.getenv('GITHUB_URL')
GITHUB_REPO = os.getenv('GITHUB_REPO')
GITHUB_OWNER = os.getenv('GITHUB_OWNER')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

if not GITHUB_URL or not GITHUB_REPO or not GITHUB_OWNER:
    logger.error("Please set the GITHUB_URL, GITHUB_REPO, and GITHUB_OWNER environment variables.")
    exit(1)

if not GITHUB_TOKEN:
    logger.error("Please set the GITHUB_TOKEN environment variable.")
    exit(1)

if not DEADLINE:
    logger.error("Please set the DEADLINE_DATE environment variable.")
    exit(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm your deadline reminder bot. Use /setdeadline YYYY-MM-DD to set a new deadline.")

async def set_deadline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        new_deadline = datetime.strptime(context.args[0], '%Y-%m-%d').date()
        global DEADLINE
        DEADLINE = new_deadline
        await update.message.reply_text(f"Deadline updated to {new_deadline}")
    except (IndexError, ValueError):
        await update.message.reply_text("Please use the format: /setdeadline YYYY-MM-DD")

async def send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    days_left = (DEADLINE - date.today()).days
    if days_left > 0:
        message = (f"⏰ *Reminder:* `{days_left}` days left until the deadline❗️\n"
                   "⏳ Time is ticking\\.\\.\\.\n"
                  f"📅 Deadline: `{DEADLINE}`\n"
                   "We got this\\! 💪\n")
    elif days_left == 0:
        message = "⚠️ *Today is the deadline❗️* ⏰"
    else:
        message = f"🚨 *The deadline has passed by* _{abs(days_left)}_ *days❗️* ⏳"

    await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN_V2)

async def manual_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_reminder(context)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_action(action=ChatAction.TYPING)

    text = "❌ \\- *Response not supported*"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2
    )

def send_request(http: urllib3.PoolManager, url: str) -> Union[None, list]:
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }


    response = http.request('GET', url, headers=headers)
    try:
        if response.status == 200:
            data = response.data.decode('utf-8')
            json_data = json.loads(data)
            return json_data
        else:
            logger.error("Failed to retrieve collaborators with status: %s", response.status)

    except MaxRetryError as e:
        logger.error("Failed to retrieve collaborators: %s", e)
    except NewConnectionError as e:
        logger.error("Failed to retrieve collaborators: %s", e)
    except HTTPError as e:
        logger.error("Failed to retrieve collaborators: %s", e)
    finally:
        if 'response' in locals():
            response.release_conn()
    return None

def get_collaborators(http: urllib3.PoolManager) -> list:
    # Add collaborators here
    url = f'{GITHUB_URL}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/collaborators'
    json_data = send_request(http, url)
    if not json_data:
        return []

    collaborators = [collaborator['login'] for collaborator in json_data]

    return collaborators

def get_deletions_additions(http: urllib3.PoolManager, commits_json: list) -> dict:
    deletions = 0
    additions = 0

    for commit in commits_json:
        url = commit['url']
        stats_commit = cast(dict, send_request(http, url))
        if not stats_commit:
            continue

        stats = stats_commit.get('stats', {})

        deletions += stats.get('deletions', 0)
        additions += stats.get('additions', 0)

    return {'deletions': deletions, 'additions': additions}

def get_commits(http: urllib3.PoolManager, collaborators: list) -> dict:

    stats = {}

    for collaborator in collaborators:
        url = f'{GITHUB_URL}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits?author={collaborator}'
        response = send_request(http, url)

        stats[collaborator] = {
            "commits": len(response),
            "deletions_additions": get_deletions_additions(http, response)
        }

    return stats

async def send_stats(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Sending stats... {context}")
    stats = context.job.data['stats']
    message = "📊 *Daily Stats* 📈\n\n\n"
    for collaborator, data in stats.items():
        message += (f"👤 *Collaborator:*   `{collaborator}`\n"
                   f"📊 *Commits:*   `{data['commits']}`\n"
                   f"🔴 *Deletions:*   `{data['deletions_additions']['deletions']}`\n"
                   f"🟢 *Additions:*   `{data['deletions_additions']['additions']}`\n\n\n")


    await context.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN_V2)

def main() -> None:
    http = urllib3.PoolManager()
    stats = {}

    collaborators = get_collaborators(http)
    if not collaborators:
        logger.info("No collaborators found.")
    else:
        stats = get_commits(http, collaborators)
        if not stats[collaborators[0]]['commits']:
            logger.info("No commits found.")
    # Build the application with the job queue


    application = ApplicationBuilder().token(TOKEN).build()

    # personal_filter = PersonalFilters()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setdeadline", set_deadline))
    application.add_handler(CommandHandler("manual_reminder", manual_reminder))
    application.add_handler(CommandHandler("daily_stats", send_stats))

    # Ensure the MessageHandler is added last
    response_handler = MessageHandler(filters.ALL, message_handler)
    application.add_handler(response_handler)

    # Schedule the daily reminder
    #application.job_queue.run_daily(send_reminder, time=time(hour=9, minute=0, second=0))
    application.job_queue.run_once(send_reminder, when=0)
    if collaborators:
        application.job_queue.run_once(send_stats, when=0, data={'stats': stats})
    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()