import genibot
from genibot.client import TwitterClient, GenerationRepository


@TwitterClient.register
class MockTwitterClient:
    def __init__(self, latest_mentions=[]):
        self.latest_mentions = latest_mentions

    def get_latest_mentions(self, most_recent_buffer_size=10):
        return self.latest_mentions

    def send_reply(self, in_reply_to_tweet_id, generation_as_bytes):
        assert generation_as_bytes is not None

        # Create fake tweet
        fake_tweet_id = 0

        # Return information about that tweet
        return {
            "tweet_id": fake_tweet_id,
        }


@GenerationRepository.register
class MockGenerationRepository:
    def __init__(self, generations={}):
        self.generations = generations

    def find_by_id(self, generation_id):
        try:
            generation = self.generations[generation_id]
        except KeyError:
            print(f"Generation with ID {generation_id} not found")
            raise 

        return generation


def test_genibot_initialization():
    empty_twitter_client = MockTwitterClient()
    empty_generation_repository = MockGenerationRepository()
    config = {
        "twitter_client": empty_twitter_client,
        "storage_client": empty_generation_repository,
    }

    bot = genibot.init(config)

    assert bot is not None


def test_bot_checks_if_there_is_a_new_tweet():
    # Setup
    latest_mentions = [{"prompt": "a beautiful face"}]
    twitter_client = MockTwitterClient(latest_mentions)
    generation_repository = MockGenerationRepository()
    config = {
        "twitter_client": twitter_client,
        "storage_client": generation_repository,
    }

    bot = genibot.init(config)

    # Action
    new_tweets = bot.check_for_new_tweets()

    # Assertions
    assert len(new_tweets) > 0


def test_bot_sends_a_new_generation():
    stored_generations = {
        "GENERATION_ID": b'generation_bytes',
    }

    config = {
        "twitter_client": MockTwitterClient(),
        "storage_client": MockGenerationRepository(stored_generations),
    }
    bot = genibot.init(config)

    generation_notification_msg = {
        "generation_id": "GENERATION_ID",
        "original_tweet_data": {
            "tweet_id": 123456,
            "tweet": "a beautiful corgi in pixel art style",
        },
    }

    # when a generation has been stored, a notification comes in that
    # says that the generation is ready to be downloaded.  Hence, is
    # ready for our bot to download the generation and send a Twitter
    # reply to the user who asked for the generation.  All of the
    # necessary information can be found in the notification message.
    generation_result = bot.send_generation(
        generation_params=generation_notification_msg,
    )

    # After the generation has been downloaded and sent, the bot will
    # have tweeted the generation and it outputs the unique generation
    # ID as well as the unique tweet ID.
    assert generation_result == {
        "generation_id": "GENERATION_ID",
        "sent_tweet_id": 0,
    }
