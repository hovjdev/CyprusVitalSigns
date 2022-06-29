import os
from dotenv import load_dotenv

load_dotenv()


UPLOAD_TO_VIMEO=True
VIMEO_TOKEN = os.getenv('VIMEO_TOKEN')
VIMEO_ID = os.getenv('VIMEO_ID')
VIMEO_SECRETS = os.getenv('VIMEO_SECRETS')

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')