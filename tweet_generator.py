# import os
# import google.generativeai as palm

# class TweetGenerator:
#     def __init__(self):
#         # Configure the palm module
#         palm_api_key = os.environ['PALM_API_KEY']
#         palm.configure(api_key=palm_api_key)
        
#     def generate_tweet_text(self, topic, description):
#         defaults = {
#           'model': 'models/text-bison-001',
#           'temperature': 0.7,
#           'candidate_count': 1,
#           'top_k': 40,
#           'top_p': 0.95,
#           'max_output_tokens': 1024,
#           'stop_sequences': [],
#           'safety_settings': [
#               {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
#               {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
#               {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 2},
#               {"category": "HARM_CATEGORY_SEXUAL", "threshold": 2},
#               {"category": "HARM_CATEGORY_MEDICAL", "threshold": 2},
#               {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 2},
#           ],
#         }
        
#         prompt = f"""Pretend to be an ancient philosopher in the modern world. Your philosophies will be reaching to billions of people in the world. So try to be as unbiased and kind as possible. You Generate just the philosophical tweet (less than 250 characters) and nothing else on the news {topic} using the {description}. Include hashtags on the topics you're tweeting.
#     Try to be satirical and leave hints for the audience to grasp your tweet. AVOID using the word "Beware" in your tweets. Be KIND and SENSITIVE and  spread POSITIVITY"""
        
#         response = palm.generate_text(
#           **defaults,
#           prompt=prompt
#         )
        
#         return response.result





import os
import google.generativeai as palm
import logging  # Importing logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Setting the log level to INFO

class TweetGenerator:
    def __init__(self):
        # Configure the palm module
        try:  # Wrapping the configuration in try block for catching any unexpected exceptions during configuration
            palm_api_key = os.environ['PALM_API_KEY']
            palm.configure(api_key=palm_api_key)
        except Exception as e:
            logger.error(f"Error configuring palm module: {str(e)}")  # Logging any unexpected error during configuration
        
    def generate_tweet_text(self, topic, description):
        try:  # Wrapping the whole method in try block for catching any unexpected exceptions
            if not topic or not description:  # Validating input
                error_message = 'Invalid topic or description'
                logger.error(error_message)  # Logging error
                return ''  # Returning empty string for invalid input
            
            defaults = {
                  'model': 'models/text-bison-001',
                  'temperature': 0.7,
                  'candidate_count': 1,
                  'top_k': 40,
                  'top_p': 0.95,
                  'max_output_tokens': 1024,
                  'stop_sequences': [],
                  'safety_settings': [
                      {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 1},
                      {"category": "HARM_CATEGORY_TOXICITY", "threshold": 1},
                      {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 1},
                      {"category": "HARM_CATEGORY_SEXUAL", "threshold": 1},
                      {"category": "HARM_CATEGORY_MEDICAL", "threshold": 1},
                      {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 1},
                  ],
                }
            
            prompt = f"""you are a witty philosopher looking at current affairs from another perspective. Try to be as unbiased and kind as possible in your tweets and make the tweets alive and interactive.
                        Rephrase the news to a meaningful context giving the actual facts and it SHOULD BE less than 250(mandatory) characters. News title, { topic }. News Description, { description }. Avoid links and INCLUDE HASHTAGS on the topics you're tweeting. add your views"""
            
            response = palm.generate_text(
                **defaults,
                prompt=prompt
            )
            
            result = response.result if hasattr(response, 'result') else ''  # Checking if result is in the response
            if not result:
                logger.warning("No result received from palm.generate_text")  # Logging a warning if no result received
            
            return result
        except Exception as e:
            error_message = f"Error generating tweet text: {str(e)}, topic: {topic}, description: {description}"
            logger.error(error_message)  # Logging any unexpected error
            return ''  # Returning empty string in case of an error
