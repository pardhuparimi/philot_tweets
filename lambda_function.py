import json
import boto3
from news_fetcher import NewsFetcher
from tweet_formatter import TweetFormatter
from image_handler import ImageHandler
from tweet_poster import TweetPoster
from tweet_generator import TweetGenerator  # Assuming TweetGenerator is in tweet_generator.py
from lambda_handler import LambdaHandler 

def lambda_handler(event, context):
    news_fetcher = NewsFetcher()
    tweet_formatter = TweetFormatter()
    image_handler = ImageHandler()
    tweet_poster = TweetPoster()
    tweet_generator=TweetGenerator()
    handler = LambdaHandler(news_fetcher,tweet_generator, tweet_formatter, image_handler, tweet_poster)
    return handler.handle(event, context)
