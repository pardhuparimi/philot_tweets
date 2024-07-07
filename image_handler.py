# import re
# import requests
# import boto3
# from requests_oauthlib import OAuth1
# import os

# class ImageHandler:
#     def __init__(self):
#         self.s3_client=boto3.client('s3')
#         self.auth = OAuth1(
#             client_key=os.environ['API_KEY'],
#             client_secret=os.environ['API_KEY_SECRET'],
#             resource_owner_key=os.environ['ACCESS_TOKEN'],
#             resource_owner_secret=os.environ['ACCESS_TOKEN_SECRET'],
#             signature_method="HMAC-SHA1"
#             )
    
        
#     def handle_image(self, image_s3_path):
#         print("s3_path ="+str(image_s3_path))
#         match = re.match(r's3://([^/]+)/(.+)', image_s3_path)
#         if not match:
#             return {'statusCode': 500, 'body': 'Invalid S3 path format'}

#         bucket_name, object_key = match.groups()
#         media_file = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
#         media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
#         files = {'media': ('image.jpeg', media_file)}
#         upload_response = requests.post(media_upload_url, files=files, auth=self.auth)

#         if upload_response.status_code != 200:
#             return {'statusCode': 500, 'body': f'Failed to upload media to Twitter: {upload_response.text}'}

#         media_id = upload_response.json().get('media_id_string')
#         return media_id


import re
import requests
import boto3
from requests_oauthlib import OAuth1
import os
import logging  # Importing logging

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Setting the log level to INFO

class ImageHandler:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.auth = OAuth1(
            client_key=os.environ['API_KEY'],
            client_secret=os.environ['API_KEY_SECRET'],
            resource_owner_key=os.environ['ACCESS_TOKEN'],
            resource_owner_secret=os.environ['ACCESS_TOKEN_SECRET'],
            signature_method="HMAC-SHA1"
        )
        
    def handle_image(self, image_s3_path):
        try:  # Wrapping the whole method in try block for catching any unexpected exceptions
            logger.info(f"s3_path = {image_s3_path}")  # Replacing print with logging
            match = re.match(r's3://([^/]+)/(.+)', image_s3_path)
            if not match:
                error_message = 'Invalid S3 path format'
                logger.error(error_message)  # Logging error
                return {'statusCode': 400, 'body': error_message}  # Changing the status code to 400 for client errors
            
            bucket_name, object_key = match.groups()
            media_file = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
            media_upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            files = {'media': ('image.jpeg', media_file)}
            upload_response = requests.post(media_upload_url, files=files, auth=self.auth)
            
            if upload_response.status_code != 200:
                error_message = f'Failed to upload media to Twitter: {upload_response.text}'
                logger.error(error_message)  # Logging error
                return {'statusCode': 500, 'body': error_message}
            
            media_id = upload_response.json().get('media_id_string')
            if not media_id:  # Checking if media_id is in the response
                error_message = 'media_id_string not received in Twitter API response'
                logger.error(error_message)  # Logging error
                return {'statusCode': 500, 'body': error_message}
            
            return media_id
        except Exception as e:
            error_message = f"Error handling image: {str(e)}, media_id: {media_id}"
            logger.error(error_message)  # Logging any unexpected error
            return {'statusCode': 500, 'body': error_message}
