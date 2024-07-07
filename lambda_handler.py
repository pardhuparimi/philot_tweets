import boto3
from requests_oauthlib import OAuth1
import os
import json
import logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LambdaHandler:
    def __init__(self, news_fetcher, tweet_generator, tweet_formatter, image_handler, tweet_poster):
        self.news_fetcher = news_fetcher
        self.tweet_formatter = tweet_formatter
        self.image_handler = image_handler
        self.tweet_poster = tweet_poster
        self.tweet_generator=tweet_generator
        self.lambda_client = boto3.client('lambda')
        
    def handle(self, event, context):
        if not event or not context:
            logger.error("Invalid event or context received")
            return {'statusCode': 400, 'body': 'Invalid event or context received'}
        
        try:
            topic, link, description = self.news_fetcher.get_trending_topic_with_link()
        except Exception as e:
            logger.error(f"Error fetching trending topic: {str(e)}")
            return {'statusCode': 500, 'body': f"Couldn't fetch a trending topic or its link: {str(e)}"}
            
        if not topic or not link:
            logger.warning("Couldn't fetch a trending topic or its link.")
            return {'statusCode': 500, 'body': "Couldn't fetch a trending topic or its link."}
        
        try:
            tweet_text = self.tweet_generator.generate_tweet_text(topic, description)
            tweet_text = self.tweet_formatter.format_tweet_text_refined(tweet_text)
        except Exception as f:
            logger.error(f"Error generating or formatting tweet text: {str(f)}")
            return {'statusCode': 500, 'body': f'Failed to generate or format tweet text: {str(f)}'}
        
        self.tweet_poster.move_article_to_newsdata(topic)
        try:
            response = self.lambda_client.invoke(
                FunctionName='arn:aws:lambda:us-east-1:739599141436:function:testbingimage',
                InvocationType='RequestResponse',
                # Payload=json.dumps({'prompt':  "generate a random image"}),
                Payload=json.dumps({'prompt':  "generate a realistic image relevant to the tweet," + tweet_text + " .Without any text on it."}),
            )
            
            # Extracting the image S3 path
            image_s3_path = json.loads(response['Payload'].read())['third_image_s3_path']
            
        except Exception as e:
            # Log the exact error returned from the invocation
            logger.error(f"Error while invoking Image Generator Lambda: {str(e)}")
            
            # Proceed to post just the tweet
            try:
                result = self.tweet_poster.post_tweet(topic, tweet_text)
               
            except Exception as p:
                logger.error(f"Error while posting the tweet: {str(p)}")
                return {'statusCode': 500, 'body': f'Failed to post the tweet: {str(p)}'}
            
            return {'statusCode': 200, 'body': f'Failed to invoke Image Generator Lambda, posted just the tweet: {str(e)}'}

        
        try:
            media_id = self.image_handler.handle_image(image_s3_path)
            if isinstance(media_id, dict) and 'statusCode' in media_id:
                return media_id
            if media_id:
                result = self.tweet_poster.post_tweet_with_media(topic, tweet_text, media_id, description,image_s3_path)
                
            else:
                result = self.tweet_poster.post_tweet(topic, tweet_text)
                
        except Exception as e:
            logger.error(f"Error handling image or posting tweet: {tweet_text}")
            try:
                result = self.tweet_poster.post_tweet(topic, tweet_text)
                
                return {'statusCode': 200, 'body': f'Failed to handle image just posted the tweet: {str(e)}'}
            except  Exception as f:
                return {'statusCode': 500, 'body': f'Failed to post the tweet: {str(f)}'}
        
        return result