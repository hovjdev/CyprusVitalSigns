import os
import sys


try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    env_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(env_path, '.env')
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.split("=")
            #print(line)
            try:
                assert len(line) == 2
            except Exception as e:
                print(str(e))
                continue
            variable = line[0].strip()
            value = line[1].strip()
            #print(f"setting: {variable}={value}")
            os.environ.setdefault(variable, value)


UPLOAD_TO_VIMEO = os.getenv('UPLOAD_TO_VIMEO')
UPLOAD_TO_VIMEO= UPLOAD_TO_VIMEO.lower() in ['true', '1', 'y', 'yes']
BLENDER_RESOLUTION_PCT = os.getenv('BLENDER_RESOLUTION_PCT')
BLENDER_RESOLUTION_PCT = int(BLENDER_RESOLUTION_PCT)


VIMEO_TOKEN = os.getenv('VIMEO_TOKEN')
VIMEO_ID = os.getenv('VIMEO_ID')
VIMEO_SECRETS = os.getenv('VIMEO_SECRETS')

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')


FLICKR_KEY=os.getenv('FLICKR_KEY')
FLICKR_SECRET=os.getenv('FLICKR_SECRET')


