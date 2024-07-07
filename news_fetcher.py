import random
import datetime
import boto3
import requests
import os
import json
import logging
import google.generativeai as palm

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Setting the log level to INFO


class NewsFetcher:
    @staticmethod
    def fetch_news():
        current_date = (datetime.datetime.utcnow() - datetime.timedelta(hours=5)).strftime('%Y-%m-%d')
        offset= 5
        # current_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        url = f"http://api.mediastack.com/v1/news?categories=science,technology&date={current_date}&offset={offset}&sort=published_desc&languages=en&access_key={os.environ['MEDIA_STACK_API_KEY']}"
        # url=f"https://api.goperigon.com/v1/all?apiKey=52246ee4-f222-4391-bb7a-435fd001b836&from=2023-11-07&country=us&sourceGroup=top100&showNumResults=true&showReprints=false&excludeLabel=Non-news&excludeLabel=Opinion&excludeLabel=Paid News&excludeLabel=Roundup&excludeLabel=Press Release&sortBy=date&category=Tech&category=Science&q=technology or science&medium=Article"
        
        response = requests.get(url)
       # logger.info(response.content)
        if response.status_code != 200:
            logger.error(f"Failed to fetch news: {response.status_code} - {response.text}")
            return None
        response_data = response.json()
        logger.info(response_data)
        return response_data.get('data', [])
    
    @staticmethod
    def is_news_interesting(news,interesting_articles):
        try:
            # Validate news data
            sanitized_title = news['title'].replace(' ', '_').replace('/', '_').replace('.', '_')
            
            # If the article already exists in the interesting articles folder, return True
            if sanitized_title in interesting_articles:
                return True
                
            # Validate news data
            if not news or not isinstance(news, dict) or not news.get('title') or not news.get('description'):
                logger.error("Invalid news data")
                return False
                
                
            defaults = {
                  'model': 'models/text-bison-001',
                  'temperature': 0,
                  'candidate_count': 1,
                  'top_k': 40,
                  'top_p': 0.95,
                  'max_output_tokens': 1024,
                  'stop_sequences': [],
                  'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":1},{"category":"HARM_CATEGORY_SEXUAL","threshold":1},{"category":"HARM_CATEGORY_MEDICAL","threshold":1},{"category":"HARM_CATEGORY_DANGEROUS","threshold":1}],
                }
                
            # Construct a suitable prompt for the Palm AI API
            prompt = f"Answer only with a 1 or 0 for True or False. Is the following news interesting and exciting for twitter engagement, {news.get('title')},{news.get('description')}. Return 1 only if it's related to science or technology or health and not a shopping or promotional news."
            
            # Configure Palm AI API Key
            palm_api_key = os.environ.get('PALM_API_KEY')
            if not palm_api_key:
                logger.error("Palm API Key is not configured")
                return False

            palm.configure(api_key=palm_api_key)
            # Placeholder for actual parameters and API call to check with Palm AI
            response = palm.generate_text(
                **defaults,
                prompt=prompt
            )
            # # Validate response
            # if response.status_code != 200:
            #     logger.error(f"Failed to check with Palm AI: {response.status_code} - {response.text}")
            #     return False
                
            try:
                result = int(response.result)
            except Exception as e:
                logger.error(f"Palm API did not return an integer: {str(e)}, news: {news}")
                return False
            
            return result
        except Exception as e:
            logger.error(f"Error checking news with Palm AI: {str(e)}, news: {news}")
            return False
    
    
    @staticmethod
    def get_articles_from_s3_folder(bucket_name, prefix):
        """Fetch all articles from a specific S3 folder and return their sanitized titles in a set."""
        s3_client = boto3.client('s3')
        articles_set = set()
        for obj in s3_client.list_objects(Bucket=bucket_name, Prefix=prefix).get('Contents', []):
            articles_set.add(obj['Key'].split('/')[-1].split('.')[0])
        return articles_set
    
    @staticmethod
    def store_and_get_interesting_article(news_list, interesting_articles, newsdata_articles, s3_client, bucket_name, interesting_prefix):
        """Store all interesting articles from a given list and return one that hasn't been tweeted yet."""
        not_tweeted_yet = None
        for news in news_list:
            sanitized_title = news['title'].replace(' ', '_').replace('/', '_').replace('.', '_')
            if sanitized_title not in interesting_articles and sanitized_title not in newsdata_articles:
                if NewsFetcher.is_news_interesting(news, interesting_articles) and sanitized_title not in interesting_articles:
                    # Store the interesting article in the "interesting articles" folder
                    object_key = f"{interesting_prefix}{sanitized_title}.json"
                    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=json.dumps(news, ensure_ascii=False))
                    if not not_tweeted_yet and sanitized_title not in newsdata_articles:
                        not_tweeted_yet = news
        return not_tweeted_yet

    @staticmethod
    def get_trending_topic_with_link():
        s3_client = boto3.client('s3')
        bucket_name = 'tweetnewsdata'
        formatted_date = (datetime.datetime.utcnow() - datetime.timedelta(hours=6)).strftime('%Y/%m/%d')
        
        interesting_prefix = f"interesting_articles/{formatted_date}/"
        newsdata_prefix = f"news_data/{formatted_date}/"
        
        # Fetch all articles from the "interesting articles" and "newsdata" folders
        interesting_articles = NewsFetcher.get_articles_from_s3_folder(bucket_name, interesting_prefix)
        newsdata_articles = NewsFetcher.get_articles_from_s3_folder(bucket_name, newsdata_prefix)
        
        # Sort the articles for newer ones first
        sorted_articles = sorted(interesting_articles, reverse=True)
        
        # Check for an article in "interesting articles" that's not in "newsdata"
        for article in sorted_articles:
            if article not in newsdata_articles:
                object_key = f"{interesting_prefix}{article}.json"
                news_data = json.loads(s3_client.get_object(Bucket=bucket_name, Key=object_key)['Body'].read())
                return news_data['title'], news_data['url'], news_data['description']
        
                # Fetch news from mediastack API in a loop with increasing offset
        # offset = 0
        # max_attempts = 1  # Let's set a limit to avoid too many API calls
        # for _ in range(max_attempts):
        news_list = NewsFetcher.fetch_news()
        # if not news_list:
        #     logger.warning(f"No news data received for offset {offset}")
            # break
        
        not_tweeted_yet = NewsFetcher.store_and_get_interesting_article(news_list, interesting_articles, newsdata_articles, s3_client, bucket_name, interesting_prefix)
        if not_tweeted_yet:
            return not_tweeted_yet['title'], not_tweeted_yet['url'], not_tweeted_yet["description"]
        
        # Increment the offset for the next API call
        # offset += 25
    
        
        logger.warning("No interesting, exciting, or new news found")
        return None, None, None