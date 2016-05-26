# Shipping a single user-specific token has limitations.
token = ''
all_messages = []
unread_messages = []


def upload(message):
    # Message: the created audio-file
    # Logic:
    # Send a REST request to the server to upload the audio file just created.
    return 0


def download():
    # Send a GET request to the server to acquire all new audio files.
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
