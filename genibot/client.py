import abc


class TwitterClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_latest_mentions(self):
        """Return the latest Twitter mentions to the bot that the bot has not
replied to yet."""

    def send_reply(self, in_reply_to_tweet_id, generation_as_bytes):
        """Sends a Twitter reply.  Needs tweet ID and a generation."""


class GenerationRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def find_by_id(self, generation_id):
        """Returns an image generation based on the ID of the generation."""


class Bot:
    def __init__(self, config):
        """Initializes a Genibot Twitter Bot client.  Requires a configuration
dictionary containing the following:

- A `TwitterClient` instance.

        """
        self.twitter_client = config["twitter_client"]
        self.generation_repository = config["storage_client"]

    def check_for_new_tweets(self):
        latest_mentions = self.twitter_client.get_latest_mentions()

        return latest_mentions

    def send_generation(self, generation_params):
        """Send a new generation to a user based on the generation
configuration."""

        # Download generation from storage (e.g. S3)
        generation_id = generation_params["generation_id"]
        generation_as_bytes = self.generation_repository.find_by_id(
            generation_id,
        )

        # Send tweet to user with generation attached
        tweet_data = generation_params["original_tweet_data"]
        twitter_username = tweet_data["username"]
        tweet_to_reply_to_id = tweet_data["tweet_id"]
        sent_tweet_data = self.twitter_client.send_reply(
            in_reply_to_tweet_id=tweet_to_reply_to_id,
            generation_as_bytes=generation_as_bytes,
        )

        # Return the ID of the generation sent and the ID of the reply
        # tweet.
        return {
            "generation_id": generation_id,
            "sent_tweet_id": sent_tweet_data["tweet_id"]
        }
            

