import RPi.GPIO as GPIO

class Controls:
    api_key = 'jay'
    host = "http://localhost:8080/"

    # Store for each matched user:
    # {
    #   user: {
    #       read  ['/path/to/audio', ...],
    #       unread['/path/to/audio', ...]
    #   },
    #   ...
    # }
    data = {}
    # Current Matched User
    cmu = None
    # Path to the current message for current user
    current_message = None
    #last recording
    recmessage = None

    #button pins
    rec_button = 7
    play_button = 11
    prev_button = 13
    next_button = 15
    proc = None
    recording = False
    playing = False
    counter = None

    def __init__(self):
        print ("Starting Client")
        self.update_state()        
        # setup pins using board numbers
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.rec_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.play_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.prev_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.next_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #GPIO.setup(self.user_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #test vars
        '''
        self.cmu = 'aare'
        self.data['aare'] = {}
        self.data['aare']['read'] = ['~/recordings/rec001.wav','~/recordings/rec002.wav','~/recordings/rec003.wav']
        self.data['aare']['unread'] = []
        self.current_message = self.data['aare']['read'][-1]
        '''


    def record(self):
        """
        Records the message when record button is held down.
        """

        if (self.recording):
            return

        import os
        import subprocess
        import time
        
        self.recmessage = 'client/audios/' + self.cmu + '/' + str(int(time.time() + (60*60))) + '.wav'
        rec = "arecord -f dat -D plughw:1,0 " + self.recmessage
        print("Recording")
        self.proc = subprocess.Popen(rec, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        self.recording = True
        #TODO start blinking the record light

    def stop_record(self):
        """
        Stops recording when button is released and then uploads an audio message.
        """
        
        if (not self.recording):
            return
        
        import os
        import signal

        
        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        #TODO stop blinking the record light
        self.recording = False
        self.proc = None
        self.__upload(self.recmessage)
        self.__notify("We have uploaded a recording")


    def play(self, channel, filepath_to_message = None):
        """
        Plays an audio message from a given path.

        Args:
            channel (int): the current pin engaged
            filepath_to_message (str): the path to the audio message.
        """

        #check if the method is initialised by the play_button 
        #check for the button again and do an early return
        if channel == self.play_button and GPIO.input(self.play_button) != False:
            return

        import subprocess

        '''
        if (self.playing):
            #if self.message:
            #    self.playing = False
            self.stop_play()
            return
        ''' 
        if not filepath_to_message:
            filepath_to_message = self.current_message
        

        play = "aplay "+ str(filepath_to_message)
        self.__notify("We are playing a recording")  
        #self.proc = subprocess.Popen(play, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
        self.proc = subprocess.call(play, shell=True)
        self.__notify("We are stopping a recording")
        #writes stdout, stderr to varible when process has ended or errored
        #self.message = self.proc.communicate()
        

    def stop_play(self):

        if (not self.playing):
            return
        
        import os
        import signal

        os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
        self.playing = False
        self.proc = None

    def next(self,channel):
        """
        Plays the next unread message (if any) for the matched user otherwise
        plays the next read message, including looping back to the start.

        Args:
            channel (int): the current pin engaged
        """
        #check for the button again
        if GPIO.input(self.next_button) != False:
            return

        if self.data[self.cmu]['unread']:
            # then add to the end of the read list and remove from unread list
            self.current_message = self.data[self.cmu]['unread'][0]
            self.data[self.cmu]['read'].append(self.data[self.cmu]['unread'][0])
            self.data[self.cmu]['unread'].pop(0)
        else:
            # Play the next message based on the position of the current read
            # Add one for comparison with len and next selection
            pos = self.data[self.cmu]['read'].index(self.current_message) + 1
            # We have read all the messages, so start from the beginning!
            if pos >= len(self.data[self.cmu]['read']):
                # Set the current message to the start message
                self.current_message = self.data[self.cmu]['read'][0]
            else:
                # Otherwise we want the next read audio
                self.current_message = self.data[self.cmu]['read'][pos]
        self.play(self.current_message)

    def previous(self, channel):
        """
        Plays the previous message for the current matched user (cmu).

        Args:
            channel (int): the current pin engaged
        """

        #check for the button again
        if GPIO.input(self.prev_button) != False:
            return

        pos = self.data[self.cmu]['read'].index(self.current_message)
        self.current_message = self.data[self.cmu]['read'][pos - 1]
        self.play(self.current_message)

    '''
    def users(self,channel):
        """
        Switches the current matched user (cmu) to the next and loops back.

        Args:
            channel (int): the current pin engaged
        """

        #check for the button again
        if GPIO.input(self.user_button) != False:
            return

        matches = [i for i in self.data.iterkeys()]

        # If there are no matches; no need to update state
        if matches:
            pos = matches.index(self.cmu) + 1
            # Ensure there are no out-of-bounds errors when the
            # last list item is checked; set next as first.
            if (pos) >= len(matches):
                self.cmu = self.data.keys()[0]
            else:
                self.cmu = self.data.keys()[pos]
            # Once the user switches we must change the current message
            if self.data[self.cmu]['read']:
                self.current_message = self.data[self.cmu]['read'][-1]
            else:
                self.current_message = self.data[self.cmu]['unread'][0]
        else:
            return
    '''
    
    def update_state(self):
        """
        Used to modify the current state for all matched users, includes:
            new matched users and unread messages
        """
        # Prevents multiple requests as we must assign cmu below
        matches = self.__matches()
        print matches
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
        elif self.data[self.cmu]['read']:
            self.current_message = self.data[self.cmu]['read'][0]
        else:
            self.__notify("There are currently no messages. Record one?")

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
        with open(filepath_to_message, 'rb') as af:
            voice_message = af.read()
        #self.recmessage = 'client/audios/' + self.cmu + '/' + str(int(time.time() + (60*60))) + '.wav'
        # NOTE: encode to binary to send with json in one request
        res = requests.post(url=self.host + "api/upload",
                            json={'sender': self.api_key,
                                  'receiver': self.cmu,
                                  'filename': filepath_to_message.split('/')[-1],
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

        res = requests.get(url=self.host + "api/matches" + "?sender=" + self.api_key)
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
        import os
        # We must create the path for when the first message is retrieved.
        matched_user_path = "client/audios/" + user
        if not os.path.exists(matched_user_path):
            os.makedirs(matched_user_path)
        # NOTE: messages are stored by token; they are unique for each conversation.
        return [f for f in os.listdir(matched_user_path) if ".wav" in f]

    def __notify(self, message):
        print "Flash: " + message                              


def main():
    # TODO: check every N minutes if there are new messages/matches:
    # invoke __update_state every 5 minutes;
    controller = Controls()
    #GPIO.add_event_detect(controller.user_button, GPIO.FALLING, callback=controller.users, bouncetime=300)
    GPIO.add_event_detect(controller.play_button, GPIO.FALLING, callback=controller.play, bouncetime=300)
    GPIO.add_event_detect(controller.prev_button, GPIO.FALLING, callback=controller.previous, bouncetime=300)
    GPIO.add_event_detect(controller.next_button, GPIO.FALLING, callback=controller.next, bouncetime=300)
    while 1:
        if (GPIO.input(controller.rec_button) == False):
            controller.record()
        else:
            controller.stop_record()


if __name__ == "__main__":
    main()
