import os
from dotenv import load_dotenv

# Retrieve environment variables from .env
load_dotenv()

# Save authentication information for retrieval from bot
consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")
access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")
bearer_token = os.getenv("bearer_token")