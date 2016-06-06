# Indeed, this is not unit-testing.
# This is to verify methods before Aare takes over.
from app import models, db

# Create the initial database from models.py
db.create_all()

# Create two unique users; a citizen and researcher
first = models.User(token="jay", role="researcher")
second = models.User(token="rem", role="citizen")
db.session.add(first)
db.session.add(second)
print "Saved two users"

# Pair these users together
pair = models.Pair(user=first, match=second)
db.session.add(pair)
print "The two users (citizen & researcher) have been paired"

import os
# We are testing with a text file, but the logic holds true
path_to_audios_in_convo = 'audios/jay_rem/'
os.makedirs(path_to_audios_in_convo)
specific_audio_to_dl = path_to_audios_in_convo + "test.wav"
# Faking upload to test download features later
open(specific_audio_to_dl, 'w').write("hello world")
im = models.Message(mid=0, message=specific_audio_to_dl,
                    status="sent", sender=first, receiver=second)
db.session.add(im)
print "An initial message has been sent by the first user."
db.session.commit()
