import abc


class TwitterClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_latest_mentions(self):
        """Return the latest Twitter mentions to the bot."""


class Bot:
    def __init__(self, config):
        """Initializes a Genibot Twitter Bot client.  Requires a configuration
dictionary containing the following:

- A `TwitterClient` instance.

        """
        self.twitter_client = config["twitter_client"]

    def check_for_new_tweets(self):
        latest_mentions = self.twitter_client.get_latest_mentions()

        return latest_mentions
