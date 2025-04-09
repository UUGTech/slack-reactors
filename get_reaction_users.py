import argparse
import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from tqdm import tqdm

"""
Script to get a list of users who reacted with a specific emoji to a Slack message

Required Slack API scopes:
- reactions:read: Access to message reaction information
- users:read: Access to user information (real_name)
- channels:history: Access to message history

Environment variables:
    SLACK_BOT_TOKEN: Slack Bot User OAuth Token

Run pip install to install the required packages:
    pip install slack-sdk tqdm

How to get the message timestamp:
    1. Copy the message link
       Example: https://your-workspace.slack.com/archives/C0123456789/p1234567890123456
    2. Get it from the last part of the URL
       - Numbers after 'p' are the timestamp
       - First 10 digits + "." + remaining 6 digits
       Example: If URL is .../p1234567890123456
           Timestamp would be 1234567890.123456
"""

# Slack API token (expected to be retrieved from environment variables)
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")


def get_reaction_users(channel_id, timestamp, reaction_name):
    """
    Get a list of users who reacted with a specific emoji to a message

    Args:
        channel_id (str): Channel ID
        timestamp (str): Message timestamp
        reaction_name (str): Emoji name (without colons)

    Returns:
        list: List of usernames who reacted
    """
    client = WebClient(token=SLACK_TOKEN)

    try:
        # Get reaction information (for public channels, can be retrieved without joining)
        print(
            f"Fetching reactions for message in channel {channel_id} at timestamp {timestamp}"
        )
        result = client.reactions_get(channel=channel_id, timestamp=timestamp)

        # Loop through all reactions in the message
        message = result["message"]
        if "reactions" in message:
            for reaction in message["reactions"]:
                if reaction["name"] == reaction_name:
                    # Get list of user IDs
                    user_ids = reaction["users"]

                    # Convert to list of usernames
                    user_names = []
                    print(
                        f"Fetching usernames for {len(user_ids)} users who reacted with :{reaction_name}:"
                    )
                    for user_id in tqdm(user_ids, desc="Fetching user info"):
                        user_info = client.users_info(user=user_id)
                        if user_info["ok"]:
                            # Get user's display name
                            if "display_name" in user_info["user"]["profile"]:
                                user_names.append(
                                    user_info["user"]["profile"]["display_name"]
                                )
                            elif "real_name" in user_info["user"]["profile"]:
                                # Use real_name if display name is not set
                                user_names.append(
                                    user_info["user"]["profile"]["real_name"]
                                )
                            else:
                                # Fallback to user ID if neither display name nor real name is set
                                user_names.append(user_info["user"]["name"])

                    return user_names

        return []

    except SlackApiError as e:
        error_message = e.response["error"]
        if error_message == "not_in_channel":
            raise ValueError(
                f"Not in channel {channel_id}. Please add your Slack App to the channel integrations."
            )
        else:
            raise ValueError(f"Slack API error: {error_message}")


def parse_slack_url(url):
    """
    Extract channel ID and timestamp from a Slack message URL

    Args:
        url (str): Slack message URL
            Example: https://workspace.slack.com/archives/C0123456789/p1234567890123456

    Returns:
        tuple: (channel_id, timestamp)
            Example: ("C0123456789", "1234567890.123456")
    """
    try:
        # Extract channel ID and timestamp parts from URL
        parts = url.split("/")
        channel_id = next(p for p in parts if p.startswith("C"))
        ts_part = next(p for p in parts if p.startswith("p"))

        # Convert timestamp to Slack format (p1234567890123456 → 1234567890.123456)
        ts_digits = ts_part[1:]  # exclude 'p'
        timestamp = f"{ts_digits[:10]}.{ts_digits[10:]}"

        return channel_id, timestamp
    except (IndexError, StopIteration):
        raise ValueError("Invalid Slack message URL format")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Get users who reacted with a specific emoji to a Slack message"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-u",
        "--url",
        help="Slack message URL (example: https://workspace.slack.com/archives/C0123456789/p1234567890123456)",
    )
    group.add_argument("-c", "--channel", help="Channel ID (example: C0123456789)")

    # timestamp is required if URL is not specified
    parser.add_argument(
        "-t",
        "--timestamp",
        help="Message timestamp (example: 1234567890.123456)",
    )
    parser.add_argument(
        "-r",
        "--reaction",
        required=True,
        help="Reaction name (example: thumbsup) Note: colons are not needed",
    )
    args = parser.parse_args()

    # If URL is specified, extract channel ID and timestamp
    if args.url:
        try:
            args.channel, args.timestamp = parse_slack_url(args.url)
        except ValueError as e:
            parser.error(str(e))
    # If URL is not specified, channel ID and timestamp are required
    elif not (args.channel and args.timestamp):
        parser.error("Channel ID and timestamp are required if URL is not specified")

    return args


def main():
    args = parse_args()

    if not SLACK_TOKEN:
        print("Error: SLACK_BOT_TOKEN environment variable is not set")
        return

    try:
        users = get_reaction_users(args.channel, args.timestamp, args.reaction)
        if users:
            print(f"\nUsers who reacted ({len(users)}):")
            for user in users:
                print(f"- {user}")
        else:
            print(f"No users found who reacted with :{args.reaction}:")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
