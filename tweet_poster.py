
import requests
from requests_oauthlib import OAuth1
import os
import logging  # Importing logging
import boto3
import datetime
import json


# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Setting the log level to INFO

s3_client = boto3.client('s3')
bucket_name = 'tweetnewsdata'
formatted_date = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime('%Y/%m/%d')
newsdata_prefix = f"news_data/{formatted_date}/"


# Updated TweetPoster class

class TweetPoster:
    def __init__(self):
        self.auth = OAuth1(
            client_key=os.environ['API_KEY'],
            client_secret=os.environ['API_KEY_SECRET'],
            resource_owner_key=os.environ['ACCESS_TOKEN'],
            resource_owner_secret=os.environ['ACCESS_TOKEN_SECRET'],
            signature_method="HMAC-SHA1"
        )
    
    def move_article_to_newsdata(self, topic):
        """Move an article from the interesting_articles folder to the news_data folder in S3."""
        sanitized_title = topic.replace(' ', '_').replace('/', '_').replace('.', '_')
        
        source_key = f"interesting_articles/{formatted_date}/{sanitized_title}.json"
        dest_key = f"{newsdata_prefix}{sanitized_title}.json"
        
        # Copy the article to the news_data folder
        s3_client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': source_key}, Key=dest_key)
        
        # Delete the article from the interesting_articles folder
        s3_client.delete_object(Bucket=bucket_name, Key=source_key)
    
    
    def post_tweet_with_media(self, topic, tweet_text, media_id, description,image_s3_path):
        try:
            if not tweet_text or not media_id:
                error_message = 'Invalid tweet_text or media_id'
                logger.error(error_message)
                return {'statusCode': 400, 'body': error_message}
            
            create_tweet_url = "https://api.twitter.com/2/tweets"
            tweet_payload = {"text": tweet_text, "media": {"media_ids": [media_id]}}
            tweet_response = requests.post(create_tweet_url, json=tweet_payload, auth=self.auth)
            
            if tweet_response.status_code < 200 or tweet_response.status_code >= 300:
                error_message = f'Failed to post tweet: {tweet_response.status_code} - {tweet_response.text}'
                logger.error(error_message)

            logger.info('Tweet posted successfully!')
            
             # Prepare the data for S3
            data = {
                "tweet_text": tweet_text,
                "description": description,
                "image_s3_path": image_s3_path
            }
            json_data = json.dumps(data)

            # Upload to S3
            sanitized_title = topic.replace(' ', '_').replace('/', '_').replace('.', '_')
        
            object_key = f"textands3path/{formatted_date}/{sanitized_title}.json"
            
            s3_client.put_object(Bucket='instadata', Key=object_key, Body=json_data)

            logger.info('Data stored in S3 successfully!')
            
            return {'statusCode': 200, 'body': 'Tweet posted successfully!'}
        except Exception as e:
            error_message = f"Error posting tweet: {str(e)}, tweet_text: {tweet_text}, media_id: {media_id}"
            logger.error(error_message)
            return {'statusCode': 500, 'body': error_message}
        
    def post_tweet(self, topic, tweet_text):
        try:
            if not tweet_text:
                error_message = 'Invalid tweet_text'
                logger.error(error_message)
                return {'statusCode': 400, 'body': error_message}
            
            create_tweet_url = "https://api.twitter.com/2/tweets"
            tweet_payload = {"text": tweet_text}
            tweet_response = requests.post(create_tweet_url, json=tweet_payload, auth=self.auth)
            
            if tweet_response.status_code < 200 or tweet_response.status_code >= 300:
                error_message = f'Failed to post tweet: {tweet_response.status_code} - {tweet_response.text}'  # Define error_message here
                logger.error(error_message)

            logger.info('Tweet posted successfully!')
            return {'statusCode': 200, 'body': 'Tweet posted successfully!'}
        except Exception as e:
            error_message = f"Error posting tweet: {str(e)}, tweet_text: {tweet_text}"
            logger.error(error_message)
            return {'statusCode': 500, 'body': error_message}
        


# This is the corrected TweetPoster class named as UpdatedTweetPoster for clarity.
