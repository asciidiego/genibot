from genibot.client import Client


def init(twitter_client):
    """Return an instance of a Genibot client."""
    return Client(twitter_client)
