# Deadline Reminder Bot

This project is a Telegram bot designed to remind users about upcoming deadlines and provide daily statistics from a GitHub repository. The bot is built using the `python-telegram-bot` library and utilizes environment variables for configuration.

## Files

### `deadline_bot.py`

This is the main script for the Deadline Reminder Bot. It includes the following functionalities:
- **Start Command**: Sends a welcome message and instructions on how to set a deadline.
- **Set Deadline Command**: Allows users to set a new deadline.
- **Send Reminder**: Sends a daily reminder about the deadline.
- **Manual Reminder**: Allows users to manually trigger a reminder.
- **GitHub Stats**: Fetches and sends daily statistics about commits, deletions, and additions from a specified GitHub repository.


### `PersonalFilters.py`

This file contains a custom message filter class for the bot:
- **PersonalFilters**: A subclass of `MessageFilter` that can be used to filter messages based on custom logic.

### `.env`

This file contains environment variables required for the bot to function. It should be filled with the appropriate values:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
DEADLINE_DATE=your_deadline_date
GITHUB_OWNER=your_github_owner
GITHUB_REPO=your_github_repo
GITHUB_URL=https://api.github.com
GITHUB_TOKEN=your_github_token
```

## Requirements

The project requires the following Python packages, as specified in the `requirements.txt` file:
- `python-telegram-bot==21.6`
- `python-telegram-bot[job-queue]==21.6`
- `python-dotenv==1.0.1`
- `urllib3==2.2.3`

## Usage

1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory and fill it with the necessary environment variables.
4. Run the bot using `python deadline_bot.py`.


## Example

Below is an example of how the bot interacts with the user. The screenshot `img.png` shows the bot in action.

![Example Reminder](img.png)

1. **Start Command**: The user initiates the bot with the `/start` command.
    - **Bot's Response**: "Hello! I'm your deadline reminder bot. Use /setdeadline YYYY-MM-DD to set a new deadline."
2. **Set Deadline Command**: The user sets a new deadline using the `/setdeadline YYYY-MM-DD` command.
    - **Bot's Response**: "Deadline updated to YYYY-MM-DD"
3. **Manual Reminder**: The user triggers a manual reminder using the `/manual_reminder` command.
    - **Bot's Response**: "Reminder: X days left until the deadline!" (or "Today is the deadline!" or "The deadline has passed by X days.")
4. **Daily Stats**: The bot sends daily statistics about commits, deletions, and additions from the specified GitHub repository.
    - **Bot's Response**: 
        ```
        📊 *Daily Stats* 📈

        👤 *Collaborator:*   `collaborator_name`
        📊 *Commits:*   `number_of_commits`
        🔴 *Deletions:*   `number_of_deletions`
        🟢 *Additions:*   `number_of_additions`
        ```

## License

This project is licensed under the MIT License.

## License

This project is licensed under the MIT License.