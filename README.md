# Slack Reaction Users Fetcher

A command-line tool to fetch a list of users who reacted with a specific emoji to a Slack message.

## Features

- Get a list of users who reacted with a specific emoji
- Support both message URL and channel ID + timestamp formats
- Show user display names (falls back to real names if display name is not set)
- Progress bar for user information fetching

## Prerequisites

### Slack App Settings

You need to create a Slack App with the following OAuth scopes:

- `reactions:read`: Access to reaction information
- `users:read`: Access to user information (for getting real names)
- `channels:history`: Access to message history

### Environment Variables

Set up your Slack Bot User OAuth Token:

```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Using Message URL

```bash
python get_reaction_users.py -u "https://your-workspace.slack.com/archives/C0123456789/p1234567890123456" -r "thumbsup"
```

### Using Channel ID and Timestamp

```bash
python get_reaction_users.py -c "C0123456789" -t "1234567890.123456" -r "thumbsup"
```

### How to Get Message Timestamp

1. Copy the message link from Slack
   - Example: `https://your-workspace.slack.com/archives/C0123456789/p1234567890123456`
2. Get the timestamp from the last part of the URL
   - Numbers after 'p' are the timestamp
   - Format: First 10 digits + "." + remaining 6 digits
   - Example: If URL ends with `p1234567890123456`, the timestamp would be `1234567890.123456`

## Error Handling

- If the Slack App is not added to the channel, you'll get a "not_in_channel" error
- If the environment variable is not set, you'll get an error message
- Invalid URL format will be caught and reported

