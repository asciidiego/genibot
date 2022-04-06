from genibot.client import Bot


def init(bot_config={}):
    """Return an instance of the Genibot bot."""

    return Bot(bot_config)
