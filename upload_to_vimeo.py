import argparse
import json
import os
from regex import P
import vimeo
import datetime
from pytz import timezone



from local_settings import VIMEO_TOKEN, VIMEO_ID, VIMEO_SECRETS, UPLOAD_TO_VIMEO

VIDEO_FILE =''
VIDEO_LIST=False
DELETE_VIDEOS=False
NB_DAYS=60


def get_videos():

    client = vimeo.VimeoClient(
    token=VIMEO_TOKEN,
    key=VIMEO_ID,
    secret=VIMEO_SECRETS)

    videos = []
    per_page = 100
    for i in range(24):
        page=i+1
        uri='/users/179570971/videos?fields=uri,name,created_time,download' +  f"&page={page}&per_page={per_page}&"  + '?sort=date'
        a=client.get(uri).json()
        print(a)
        if 'data' in a:
            videos.extend(a['data'])
        else:
            break
    return videos


def delete_videos(video_list, nb_days=NB_DAYS):

    print(f"Deleting videos older than {NB_DAYS}")
    
    to_delete=[]
    for v in video_list:
        now = datetime.datetime.now(tz=timezone('EET'))
        date = datetime.datetime.fromisoformat(v['created_time'])
        timedelta = now - date
        do_delete=False
        if timedelta.days > nb_days:
            do_delete=True
            to_delete.append(v)
        print(v['uri'], 'is', timedelta.days, 'days old.', 'Delete', do_delete)




    client = vimeo.VimeoClient(
    token=VIMEO_TOKEN,
    key=VIMEO_ID,
    secret=VIMEO_SECRETS)


    for v in to_delete:
        print(f"Deleting {v['uri']}...")
        uri=f"{v['uri']}"
        a=client.delete(uri)
        print(a)


def upload_mp4_to_vimeo(video_file_path, data, upload_to_vimeo=UPLOAD_TO_VIMEO):

    if upload_to_vimeo==False:
        print(f"UPLOAD_TO_VIMEO: {UPLOAD_TO_VIMEO}")
        print(f"UPLOAD_TO_VIMEO is set in local_settings.py")
        return

    # Instantiate the library with your client id, secret and access token
    # (pulled from dev site)
    client = vimeo.VimeoClient(
        token=VIMEO_TOKEN,
        key=VIMEO_ID,
        secret=VIMEO_SECRETS,
    )

    print('Uploading: %s' % video_file_path)

    try:

        name = data['video_title']
        description = ' '.join(data['video_tags'])

        # Upload the file and include the video title and description.
        uri = client.upload(video_file_path, data={
            'name': name,
            'description': description
        })
        print(f'uri, {uri}')

        # Get the metadata response from the upload and log out the Vimeo.com url
        video_data = client.get(uri + '?fields=link').json()
        print('"{}" has been uploaded to {}'.format(video_file_path, video_data['link']))

        if False:
            # Make an API call to edit the title and description of the video.
            client.patch(uri, data={
                'name': name,
                'description': description})

            print('The title and description for %s has been edited.' % uri)

            # Make an API call to see if the video is finished transcoding.
            video_data = client.get(uri + '?fields=transcode.status').json()
            print('The transcode status for {} is: {}'.format(
                uri,
                video_data['transcode']['status']
            ))
    except Exception as e:
        # We may have had an error. We can't resolve it here necessarily, so
        # report it to the user.
        print(str(e))
        print('Error uploading %s' % video_file_path)

    return


if __name__ == "__main__":


    # Initialize parser
    parser = argparse.ArgumentParser()
    
    # Adding optional argument
    parser.add_argument("-vf", "--video_file", help = 'Provide the video file you wish to upload. Default: ""')
    parser.add_argument("-l", "--list", help = 'Get a list of uploaded videos',  action='store_true')
    parser.add_argument("-d", "--delete", help = f'Delete videos older than this number of days.')

    
    # Read arguments from command line
    args = parser.parse_args()
    
    if args.video_file:
        VIDEO_FILE=args.video_file

    if args.list:
        VIDEO_LIST=True

    if args.delete:
        DELETE_VIDEOS=True
        NB_DAYS=int(args.delete)

    print(f"VIDEO_FILE: {VIDEO_FILE}")
    print(f"VIDEO_LIST: {VIDEO_LIST}")
    print(f"DELETE_VIDEOS: {DELETE_VIDEOS}")
    print(f"NB_DAYS: {NB_DAYS}")


    if VIDEO_FILE != '':

        if not os.path.exists(VIDEO_FILE):
            print(f"File doesn't exist: {VIDEO_FILE}")
            exit(1)


        data={
                'video_title': 'Cyprus Vital Signs',
                'video_file_path': VIDEO_FILE,
                'video_tags': 'Cyprus Vital Signs',
                'video_thumbnail_path': None,
                'public': False,
                'playlist_name': None
            }
        upload_mp4_to_vimeo(VIDEO_FILE, data)



    if VIDEO_LIST:
        video_list = get_videos()
        print(video_list)


    if DELETE_VIDEOS:
        video_list = get_videos()
        delete_videos(video_list, nb_days=NB_DAYS)


