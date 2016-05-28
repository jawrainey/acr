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


def __save(receiver, message):
    import os
    import time
    ufiles = "audios/" + receiver

    # For when a user first publishes a file.
    if not os.path.exists(ufiles):
        os.makedirs(ufiles)

    path = ufiles + "/" + str(int((time.time() + (60*60))))
    with open(path, 'wb') as f:
        f.write(message)


def previous(receiver, current):  # Similar logic for next()
    # Grab the list of local files
    # Sort into DESC order (they are UNIX timestamps)
    # Find location of current - 1
    # invoke play method
    # current - 1
    return


def __matches():
    # Determine who we are communicating with
    # invoke matches API that should return
    # a list of all the users you can talk with.
    return 0


def record(current):
    # Determine who we are communicating with
    # Take input from the microphone and save to local file
    # locally token/<receiver>
    # Upload data the server
    # Flash light to notify success/failure
    return


def play():
    # Determine who we are communicating with
    # Download all latest (not local) audio messages
    # If there are new files: invoke next(current)
    # Otherwise, play current
    # TODO: helper method to play an audio-file on pi
    return


def next_user():
    # The "User" button will allow the user (button presser) to go through all
    # the users that they are matched with. Therefore, the above buttons all
    # take the user as parameter.
    return 0


def notify():
    # Change light based on action?
    # Input could be a list that represents a pattern
    # of actions -- similar to noises for BIOS?
    return 0


def main():
    # Run every 5 minutes to check for new new audios (download_audio)
    # if there is an audio: download the audio, then send a notification
    return 0

if __name__ == "__main__":
    __upload('/Users/b5060990/Desktop/1464205566000', 'bob')
