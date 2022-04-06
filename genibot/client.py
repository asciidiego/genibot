import abc


class TwitterClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_latest_mentions(self):
        """Return the latest Twitter mentions to the bot."""


class Client:
    def __init__(self, twitter_client=None):
        """Initializes a Genibot Twitter Bot client.  Requires a Twitter
Client.

        """
        self.twitter_client = twitter_client

    def check_for_new_tweets(self):
        latest_mentions = self.twitter_client.get_latest_mentions()

        return latest_mentions
