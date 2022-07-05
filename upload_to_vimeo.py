import json
import os
import vimeo

from local_settings import VIMEO_TOKEN, VIMEO_ID, VIMEO_SECRETS, UPLOAD_TO_VIMEO


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

        output_video='output/cvs_data_vids/379e863fbd7e4f01b76f44aaf4ea46ca/video.mp4'

        data={
                'video_title': 'Cyprus Vital Signs',
                'video_file_path': output_video,
                'video_tags': 'Cyprus Vital Signs',
                'video_thumbnail_path': None,
                'public': False,
                'playlist_name': None
            }
        upload_mp4_to_vimeo(output_video, data)