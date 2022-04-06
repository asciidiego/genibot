import genibot
from genibot.client import TwitterClient

@TwitterClient.register
class MockTwitterClient:
    def __init__(self, latest_mentions=[]):
        self.latest_mentions = latest_mentions

    def get_latest_mentions(self):
        return self.latest_mentions


def test_genibot_module_is_imported_correctly():
    assert genibot is not None


def test_genibot_initialization():
    empty_twitter_client = MockTwitterClient()
    config = {"twitter_client": empty_twitter_client}

    bot = genibot.init(config)

    assert bot is not None


def test_bot_checks_if_there_is_a_new_tweet():
    # Setup
    latest_mentions = [{"prompt": "a beautiful face"}]
    twitter_client = MockTwitterClient(latest_mentions)
    config = {"twitter_client": twitter_client}

    bot = genibot.init(config)

    # Action
    new_tweets = bot.check_for_new_tweets()

    # Assertions
    assert len(new_tweets) > 0
