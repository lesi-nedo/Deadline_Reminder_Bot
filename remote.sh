#!/bin/bash

REMOTE_USER="bitnami"
REMOTE_IP="3.67.160.120"
REMOTE_PORT="2222"
REMOTE_DIR="/home/bitnami/telegram_bots/bots/deadline_reminder"
PEM_FILE="/home/lesi-nedo/Desktop/website/mywebsite/nedo.pem"
SSH_OPTIONS="-p $REMOTE_PORT -i $PEM_FILE"

ITEMS_TO_TRANSFER=(
  "PersonalFilters.py"
  "deadline_bot.py"
  "requirements.txt"
)

RSYNC_OPTIONS=(
  "-avz"
  "--progress"
  "--exclude=__pycache__"
  "--exclude=.git"
  "--exclude=.idea"
)

item_exists() {
  if [ ! -e "$1" ]; then
    echo "Error: $1 does not exist"
    return 1
  fi
  return 0
}

check_pem_file() {
  if [ ! -f "$PEM_FILE" ]; then
    echo "Error: PEM file does not exist"
    exit 1
  fi
  if [ "$(stat -c %a "$PEM_FILE")" != "600" ]; then
    echo "Warning: Incorrect permissions for PEM file. It should be 600. Changing permissions..."
    chmod 600 "$PEM_FILE"
  fi
}

echo "Starting file transfer to remote machine using rsync..."

# Call the check_pem_file function
check_pem_file

for item in "${ITEMS_TO_TRANSFER[@]}"; do
  if item_exists "$item"; then
    echo "Transferring $item..."
    rsync "${RSYNC_OPTIONS[@]}" -e "ssh $SSH_OPTIONS" "$item" "$REMOTE_USER@$REMOTE_IP:$REMOTE_DIR"
    if [ $? -eq 0 ]; then
      echo "Successfully transferred $item"
    else
      echo "Error: failed to transfer $item"
    fi
  fi
done
