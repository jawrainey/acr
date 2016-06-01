class Controls:
    # These could be in a config file, but #YOLO
    api_key = 'helloworld'
    host = "http://localhost:8080/"

    # Store for each matched user:
    # {{ user: {read ['/path/to/audio1', ...], unread[]}, ... }
    data = {}
    # Current Matched User
    cmu = None
    # Path to the current message for current user
    current_message = None

    def __init__(self):
        self.__update_state()
        # Last user matched is the current
        self.cmu = self.matched_users[-1]

    def record(self):
        message = "path/to/recording"
        self.__save(message)
        self.__upload(message)
        self.notify("We have uploaded a recording")

    def play(self, filename):
        import subprocess
        subprocess.call(["afplay", filename])
        self.notify("We are playing a recording")

    def next(self):
        if self.unread_messages:
            # then add to the end of the read list and remove from unread list
            self.current_message = self.data[self.cmu]['unread'][0]
            self.data[self.cmu]['read'].append(self.data[self.cmu]['unread'][0])
            self.data[self.cmu]['unread'].pop(-1)
        else:
            # Play the next message based on the position of the current read
            pos = self.data[self.cmu]['read'].index(self.current_message) + 1
            # We have read all the messages
            if pos >= len(self.data[self.cmu]['read']):
                # Set the current message to the start message
                self.current_message = self.data[self.cmu]['read'][-1]
            else:
                # Otherwise we want the next read audio
                self.current_message = self.data[self.cmu]['read'][pos + 1]
        self.play(self.current_message)

    def previous(self):
        # Play the previous message based on the current message
        self.play(self.data[self.cmu]['read'][
                      self.data[self.cmu]['read'].index(self.current_message) - 1])

    def users(self):
        # This method grabs data for the NEXT users
        cur_pos = [i for i in self.data.iterkeys()].index(self.cmu)
        # Ensure there are no out-of-bounds errors
        if (cur_pos + 1) >= len(self.data):
            self.cmu = self.data.keys()[0]
        else:
            self.cmu = self.data.keys(cur_pos + 1)
        self.current_message = self.data[self.cmu]['read'][-1]

    def __upload(self, audio_file):
        import base64
        import time
        import requests

        # NOTE: messages are stored locally for instant playback and browsing.
        with open(audio_file, 'rb') as af:
            voice_message = af.read()

        # NOTE: encode to binary to send with json in one request
        res = requests.post(url=self.host + "api/upload",
                            json={'sender': self.api_key,
                                  'receiver': self.cmu,
                                  'filename': str(int((time.time() + (60*60)))),
                                  'message': base64.b64encode(voice_message)},
                            headers={'Content-Type': 'application/json'})

        if res.status_code is not 201:
            print "TODO: blink a red light."

    def __unread_messages(self, receiver, latest_message_name):
        import requests
        data = ("?sender=" + self.api_key +
                "&receiver=" + receiver +
                "&latest=" + latest_message_name)
        res = requests.get(url=self.host + "api/download" + data)

        if res.status_code == 200:
            import io
            import zipfile
            # In memory-stream used as ZipFile constructor expects a file.
            # Prevents a zip file being saved locally that need not be removed.
            path = 'audios/' + self.receiver + '/'
            with zipfile.ZipFile(io.BytesIO(res.content), 'r') as zf:
                zf.extractall(path)
            # ??
            return [path + fname for fname in zf.namelist()]
        else:
            print "TODO: blink a red light."

    def __matches(self):
        import json
        import requests

        res = requests.get(url=self.host + "api/matches" + "?user=" + self.api_key)
        return json.loads(res.content)['matches']

    def __all_messages(self, user):
        # TODO: this should exclude unread messages if they have not been read!
        import os
        return [f for f in os.listdir("audios/" + user) if ".ogg" in f]

    def __save(self, message):
        import os
        import time
        ufiles = "audios/" + self.cmu

        # For when a user first publishes a file.
        if not os.path.exists(ufiles):
            os.makedirs(ufiles)

        path = ufiles + "/" + str(int((time.time() + (60*60))))
        with open(path, 'wb') as f:
            f.write(message)

    def __update_state(self):
        for user in self.__matches():
            # As there may be multiple conversations user => matches
            # We must find all read/unread for each conversation.
            self.data[user] = {
                'read': self.all_messages(user),
                'unread': self.__unread_messages(
                    user, len(self.data[user]['read']))}

    def __notify(self, message):
        print "Flash: " + message


def main():
    # Check every N minutes if there are new messages/matches:
    # invoke __update_state every 5 minutes;
    controller = Controls()

if __name__ == "__main__":
    main()