# Changelog

## [1.1.1] - 2024-10-6
### Changes
- Environment variable loading now supports specifying a file, enhancing flexibility for different deployment scenarios.
- Introduced `_send_message` function to centralize message sending and manage exceptions related to chat migration.
- Improved the scheduling of daily reminders, setting specific times for notifications.
- Polling interval adjusted to 43200 seconds, ensuring less frequent API calls.
- Enhanced logging for better debugging and monitoring of API interactions.

