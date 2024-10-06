#! /bin/bash

SCRIPT_PATH=$(dirname $(readlink -f $0))
SCRIPT_FILE_NAME="deadline_bot.py"
LOG_FILE_NAME="deadline_bot.log"
DEFAULT_ENV_FILE="/home/lesi-nedo/Desktop/telegram_bots/envs/.env_test"
DEFAULT_VENV_PATH="/home/lesi-nedo/miniforge3/envs/telegram_bots"



if [ "$#" -ne 2 ]; then
    echo -e "\e[31mUsing Default Paths\e[0m  [\e[36mUsage: $0 <abs_path_to_env_file> <abs_path_to_venv>\e[0m]"
    ENV_FILE=$DEFAULT_ENV_FILE
    VENV_PATH=$DEFAULT_VENV_PATH
else
    ENV_FILE=$1
    VENV_PATH=$2
fi


if [ ! -f "$ENV_FILE" ]; then
    echo "File $1 does not exist"
    exit 1
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "Directory $2 does not exist"
    exit 1
fi

SCRIPT_FILE="$SCRIPT_PATH/$SCRIPT_FILE_NAME"


TEMP_CRON=$(mktemp)

crontab -l > "$TEMP_CRON" 2>/dev/null

mkdir -p "$SCRIPT_PATH/logs"
echo -e "\e[32mLog file path: $SCRIPT_PATH/logs/$LOG_FILE_NAME\e[0m"

LOG_PATH="$SCRIPT_PATH/logs/$LOG_FILE_NAME"

echo "# Telegram Bot Reminder -- runs dayly at 9:00 AM" >> "$TEMP_CRON"
echo "0 9 * * * $VENV_PATH/bin/python $SCRIPT_FILE $ENV_FILE cron reminder >> $LOG_PATH" >> "$TEMP_CRON"
echo "# Telegram Bot Stats -- runs dayly at 9:00 PM" >> "$TEMP_CRON"
echo "0 21 * * * $VENV_PATH/bin/python $SCRIPT_FILE $ENV_FILE cron stats >> $LOG_PATH" >> "$TEMP_CRON"

crontab "$TEMP_CRON"

rm "$TEMP_CRON"

echo "Crontab task set successfully"