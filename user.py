# Shipping a single user-specific token has limitations.

# TODO: write script to invoke this script once pi boots.
# TODO: who is going to configure the WiFi?

API_KEY = 'helloworld'
all_messages = []
unread_messages = []
HOST = "http://localhost:8080/"


def __upload(audio_file, receiver):
    import base64
    import time
    import requests

    # NOTE: messages are stored locally to support playback, browsing & backup.
    with open(audio_file, 'rb') as af:
        voice_message = af.read()

    # NOTE: encode to binary to send with json in one request
    res = requests.post(url=HOST + "api/upload",
                        json={'sender': API_KEY,
                              'receiver': receiver,
                              'filename': str(int((time.time() + (60*60)))),
                              'message': base64.b64encode(voice_message)},
                        headers={'Content-Type': 'application/json'})

    if res.status_code is not 201:
        print "TODO: blink a red light."


def __download(receiver, latest_message_name):
    import requests
    data = ("?sender=" + API_KEY +
            "&receiver=" + receiver +
            "&latest=" + latest_message_name)
    res = requests.get(url=HOST + "api/download" + data)

    if res.status_code == 200:
        import io
        import zipfile
        # In memory-stream used as ZipFile constructor expects a file.
        # Prevents a zip file being saved locally that would need to be removed.
        with zipfile.ZipFile(io.BytesIO(res.content), 'r') as zf:
            zf.extractall('audios/' + receiver + '/')
        # TODO: notify user that new message(s) received (see: # zf.namelist())
    else:
        print "TODO: blink a red light."
    return 0


def controls():
    # Note: the user would have all the audios stored on their device.
    # A copy is stored in the database encase of failure.
    # When they press "Next" or "Previous" they go through their stored audios.

    # The "Record" button will record an audio, then invoke upload_audio()

    # The "Notify" icon

    # The "Play" button will play the latest audio.

    # The "User" button will allow the user (button presser) to go through all
    # the users that they are matched with. Therefore, the above buttons all
    # take the user as parameter.
    return 0


def main():
    # Run every 5 minutes to check for new new audios (download_audio)
    # if there is an audio: download the audio, then send a notification
    return 0

if __name__ == "__main__":
    __upload('/Users/b5060990/Desktop/1464205566000', 'bob')
