

# import re
# import logging  # Importing logging

# # Setup logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)  # Setting the log level to INFO

# class TweetFormatter:
#     @staticmethod
#     def format_tweet_text_refined(result):
#         try:  # Wrapping the whole method in try block for catching any unexpected exceptions
#             if not isinstance(result, str):  # Validating input type
#                 error_message = f"Invalid input type: {type(result)}, expected str"
#                 logger.error(error_message)  # Logging error
#                 return result  # Return the original input if it is not a string
            
#             tweet_text = result
#             tweet_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', tweet_text)
#             tweet_text = tweet_text.replace('*', '')
#             tweet_text = re.sub(r'[^a-zA-Z0-9\s#.,]', '', tweet_text)
#             components = tweet_text.split()
#             words = [comp for comp in components if not comp.startswith('#')]
#             hashtags = [comp for comp in components if comp.startswith('#')]
#             reconstructed_text = ' '.join(words).strip('"*') + ' ' + ' '.join(hashtags)
#             return reconstructed_text
#             return reconstructed_text
#         except Exception as e:
#             error_message = f"Error formatting tweet text: {str(e)}, input: {result}"
#             logger.error(error_message)  # Logging any unexpected error
#             return result  # Return the original input in case of an error




import os
import re
import logging  # Importing logging
import google.generativeai as palm
palm_api_key = os.environ['PALM_API_KEY']
palm.configure(api_key=palm_api_key)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Setting the log level to INFO

class TweetFormatter:
    @staticmethod
    def format_tweet_text_refined(result):
        try:  # Wrapping the whole method in try block for catching any unexpected exceptions
            if not isinstance(result, str):  # Validating input type
                error_message = f"Invalid input type: {type(result)}, expected str"
                logger.error(error_message)  # Logging error
                return result  # Return the original input if it is not a string
            
            defaults = {
              'model': 'models/text-bison-001',
              'temperature': 0,
              'candidate_count': 1,
              'top_k': 40,
              'top_p': 0.95,
              'max_output_tokens': 1024,
              'stop_sequences': [],
              'safety_settings': [{"category":"HARM_CATEGORY_DEROGATORY","threshold":1},{"category":"HARM_CATEGORY_TOXICITY","threshold":1},{"category":"HARM_CATEGORY_VIOLENCE","threshold":2},{"category":"HARM_CATEGORY_SEXUAL","threshold":2},{"category":"HARM_CATEGORY_MEDICAL","threshold":2},{"category":"HARM_CATEGORY_DANGEROUS","threshold":2}],
                }
                
            prompt = f"""{result}.remove any * or ** and replace &amp; with &  format and rephrase the above into a meaningful tweet suitable to be posted directly on my behalf and remove any extra punctuations.dont explicitly mention anything related to philosophy. the tweet should be less than 250 characters"""

            response = palm.generate_text(
              **defaults,
              prompt=prompt
            )
            return response.result.replace('&amp;','&').replace('*','')
        except Exception as e:
            error_message = f"Error formatting tweet text: {str(e)}, input: {result}"
            logger.error(error_message)  # Logging any unexpected error
            return result  # Return the original input in case of an error

