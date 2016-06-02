class Controls:
    api_key = 'jay'
    host = "http://localhost:8080/"

    # Store for each matched user:
    # {{ user: {read ['/path/to/audio1', ...], unread[]}, ... }
    data = {}
    # Current Matched User
    cmu = None
    # Path to the current message for current user
    current_message = None

    def __init__(self):
        self.update_state()

    def record(self):
        """
        Records, saves then uploads an audio message.
        """
        message = "path/to/recording"
        self.__save(message)
        self.__upload(message)
        self.__notify("We have uploaded a recording")

    def play(self, filepath_to_message):
        """
        Plays an audio message from a given path.

        Args:
            filepath_to_message (str): the path to the audio message.
        """
        import subprocess
        subprocess.call(["afplay", filepath])
        self.__notify("We are playing a recording")

    def next(self):
        """
        Plays the next unread message (if any) for the matched user otherwise
        plays the next read message, including looping back to the start.
        """
        if self.data[self.cmu]['unread']:
            # then add to the end of the read list and remove from unread list
            self.current_message = self.data[self.cmu]['unread'][0]
            self.data[self.cmu]['read'].append(self.data[self.cmu]['unread'][0])
            self.data[self.cmu]['unread'].pop(0)
        else:
            # Play the next message based on the position of the current read
            pos = self.data[self.cmu]['read'].index(self.current_message)
            # We have read all the messages, so start from the beginning!
            if pos >= len(self.data[self.cmu]['read']):
                # Set the current message to the start message
                self.current_message = self.data[self.cmu]['read'][0]
            else:
                # Otherwise we want the next read audio
                self.current_message = self.data[self.cmu]['read'][pos + 1]
        self.play(self.current_message)

    def previous(self):
        """
        Plays the previous message for the current matched user (cmu).
        """
        pos = self.data[self.cmu]['read'].index(self.current_message)
        prev_msg = self.data[self.cmu]['read'][pos - 1]
        self.current_message = prev_msg
        self.play(self.current_message)

    def users(self):
        """
        Switches the current matched user (cmu) to the next and loops back.
        """
        matches = [i for i in self.data.iterkeys()]
        # If there are no matches; no need to update state
        if matches <= 1:
            return
        else:
            cur_pos = matches.index(self.cmu)
            # Ensure there are no out-of-bounds errors when the
            # last list item is checked; set next as first.
            if (cur_pos + 1) >= len(matches):
                self.cmu = self.data.keys()[0]
            else:
                self.cmu = self.data.keys(cur_pos + 1)
            self.current_message = self.data[self.cmu]['read'][-1]

    def update_state(self):
        """
        Used to modify the current state for all matched users, includes:
            new matched users and unread messages
        """
        # Prevents multiple requests as we must assign cmu below
        matches = self.__matches()

        for user in matches:
            # As there may be multiple conversations user => matches
            # We must find all read/unread for each conversation.
            am = self.__all_messages(user)
            self.data[user] = {
                'read': am,
                'unread': self.__unread_messages(user, len(am))}
        # This assumes we are matched with at least one, which is
        # true given we will send an artefact to a users home!
        self.cmu = matches[-1]

        if self.data[self.cmu]['unread']:
            self.current_message = self.data[self.cmu]['unread'][0]
        else:
            self.current_message = self.data[self.cmu]['read'][0]

    def __upload(self, filepath_to_message):
        """
        Uploads the users audio message to the server from a given path,
        which uses the current matched user within the request.

        Args:
            filepath_to_message (str): the path to the audio message.
        """
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
            print "TODO: blink a red light for UPLOAD."

    def __unread_messages(self, receiver, number_of_messages):
        """
        Used to request and download unread messages for a given conversation.
        Messages are streamed and unzipped in memory and stored locally in a
        unique folder representing a conversation, i.e. client_receiver

        Args:
            receiver (str): the other user in the conversation.
            num_messages (int): the number of messages in a conversation with receiver.

        Returns:
            list: The paths to the unread (new) audio messages by the receiver.
        """
        import requests

        data = ("?sender=" + self.api_key +
                "&receiver=" + receiver +
                "&latest=" + str(number_of_messages))
        res = requests.get(url=self.host + "api/download" + data)

        if res.status_code == 200:
            import io
            import zipfile
            # In memory-stream used as ZipFile constructor expects a file.
            # Prevents a zip file being saved locally that need not be removed.
            path = 'client/audios/' + receiver + '/'
            with zipfile.ZipFile(io.BytesIO(res.content), 'r') as zf:
                zf.extractall(path)
            # A list of locations to unread messages from sender to receiver
            return [path + fname for fname in zf.namelist()]
        elif res.status_code == 204:
            print "Note: there are no new messages to download"
        else:
            print "TODO: blink a red light for DOWNLOAD."

    def __matches(self):
        """
        Determines who is matched with the client -- they who own the pi.
        This is used when initialising and updating the client's state.

        Returns:
            list: the unique identifies (tokens) of the matched users
        """
        import json
        import requests

        res = requests.get(url=self.host + "api/matches" + "?user=" + self.api_key)
        # TODO: our service returns unicode; we could simplify this to strings.
        return [str(match) for match in json.loads(res.content)['matches']]

    def __all_messages(self, user):
        """
        Obtains a list of paths to all audios messages in a conversation
        between the client and a specific user.

        Args:
            user (str): the token of the user to search for

        Returns:
            list: a list paths to each message in the conversation.
        """
        # TODO: this should exclude unread messages if they have not been read!
        import os
        # NOTE: messages are stored by token; they are unique for each conversation.
        return [f for f in os.listdir("client/audios/" + user) if ".ogg" in f]

    def __save(self, filepath_to_message):
        """
        Saves a recorded audio message.

        Args:
            filepath_to_message (str): the path to the audio message.
        """
        import os
        import time
        # Store the messages (sent/received) by token to represent a conversation.
        ufiles = "client/audios/" + self.cmu

        # For when a user first publishes a file.
        if not os.path.exists(ufiles):
            os.makedirs(ufiles)

        path = ufiles + "/" + str(int((time.time() + (60*60))))
        with open(path, 'wb') as f:
            f.write(filepath_to_message)

    def __notify(self, message):
        print "Flash: " + message


def main():
    # TODO: check every N minutes if there are new messages/matches:
    # invoke __update_state every 5 minutes;
    controller = Controls()

if __name__ == "__main__":
    main()
