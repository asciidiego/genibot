import io
import os
import time
import json
import boto3
import redis
import tweepy
import genibot
from PIL import Image
from threading import Timer

from genibot.client import TwitterClient, GenerationScheduler, GenerationRepository

ENV_VARS = {"PUBSUB_HOST", "PUBSUB_PORT"}
print("Getting environment variables from:")
print(ENV_VARS)

PUBSUB_HOST = os.getenv("PUBSUB_HOST", 'localhost')
PUBSUB_PORT = os.getenv("PUBSUB_PORT", 6379)

TWITTER_KEYS = {
    "consumer_key": os.getenv("TWITTER_API_KEY"),
    "consumer_secret": os.getenv("TWITTER_API_KEY_SECRET"),
    "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
    "bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
}

redis = redis.Redis(
    host=PUBSUB_HOST,
    port=PUBSUB_PORT,
    db=0,
)
pubsub = redis.pubsub()


@GenerationRepository.register
class S3GenerationRepository:
    def __init__(self, region_name, bucket_name):
        self.s3 = boto3.client("s3", region_name=region_name)
        self.bucket_name = bucket_name

    def find_by_id(self, generation_id):
        s3_response_object = self.s3.get_object(
            Bucket=self.bucket_name,
            Key=generation_id,
        )
        object_content = s3_response_object['Body'].read()
        bytes_buffer = io.BytesIO(object_content)

        return bytes_buffer
        

@GenerationScheduler.register
class RedisScheduler:
    def __init__(self, redis_conn, channel):
        self.redis_client = redis_conn
        self.scheduler_channel = channel

    def schedule_generation_job(self, job_data):
        serialized_job_data = json.dumps(job_data)
        self.redis_client.lpush(self.scheduler_channel, serialized_job_data)


class TwitterStreamHandler(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        job_data = {
            "id": str(tweet.id),
            "text": tweet.text.replace("@genibot", "").replace("#geni", ""),
        }
            

        pubsub.subscribe(**{job_data["id"]: on_generation_finished})

        scheduler.schedule_generation_job(job_data)

        thread = pubsub.run_in_thread(sleep_time=0.001)

        def close_thread():
            print("Closing thread for ID: ", job_data["id"])
            thread.stop()

        # close thread after 30 seconds
        Timer(30.0, close_thread).start()


@TwitterClient.register
class TwitterClientImpl:
    def __init__(self, keys):
        assert keys is not None, "need Twitter credentials"
        self.stream_client = TwitterStreamHandler(
            keys["bearer_token"],
        )
        v1_auth = tweepy.OAuth1UserHandler(
            keys["consumer_key"],
            keys["consumer_secret"],
            keys["access_token"],
            keys["access_token_secret"],
        )
        self.api_v1 = tweepy.API(v1_auth)

    def send_reply(self, in_reply_to_tweet_id, generation_as_bytes):
        img = Image.open(generation_as_bytes)
        img_filename = f"{in_reply_to_tweet_id}.png"
        img.save(img_filename)
        generation_as_twitter_media =self.api_v1.media_upload(
            filename=img_filename,
        )

        self.api_v1.update_status(
            status="",
            in_reply_to_status_id=in_reply_to_tweet_id,
            media_ids=[generation_as_twitter_media.media_id],
            auto_populate_reply_metadata=True,
        )
    

    def start(self):
        self.stream_client.filter()

scheduler = RedisScheduler(redis, "ldm")
generation_repository = S3GenerationRepository(
    region_name="us-west-2",
    bucket_name="genibot",
)
twitter_client = TwitterClientImpl(TWITTER_KEYS)
bot = genibot.init({
    "twitter_client": twitter_client,
    "storage_client": generation_repository,
    "generation_scheduler": scheduler,
})


def on_generation_finished(message):
    # subscribe ACK
    if message["data"] == 1:
        print("subscribed successfully to tweet job")
        return

    generation_data = json.loads(message['data'])

    tweet_id = message["channel"]
    generation_id = generation_data["imgId"]

    generation_params = {
        "generation_id": generation_id,
        "original_tweet_data": {
            "tweet_id": tweet_id.decode(),
        }
    }

    bot.send_generation(generation_params)
    



if __name__ == "__main__":
    twitter_client.start()

