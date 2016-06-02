# Indeed, this is not unit-testing.
# This is to verify methods before Aare takes over.
from app import models, db

# Create the initial database from models.py
db.create_all()
# A matched pair of citizens
first  = models.User(token="jay", role="researcher")
second = models.User(token="rem", role="citizen")
db.session.add(first)
db.session.add(second)
print "Saved two users"
pair = models.Pair(user=first, match=second)
db.session.add(pair)
print "The two users (citizen & researcher) have been paired"
print "TODO: put a file inside client/audios/rem"
im = models.Message(mid=0, message="audios/rem/1",
                    status="sent", sender=first, receiver=second)
db.session.add(im)
print "An initial message has been sent by the first user."
db.session.commit()