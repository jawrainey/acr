from flask import request, abort, jsonify
from app import app


@app.route('/api/download', methods=['GET'])
def download(token):
    # Token: who is the user?
    # Algorithm: find NEW audios for user; those they are matched to.
    # Return: audio file from matched user(s) (or download URIs?)

    # Ask the server every N seconds if a new message has been received for
    # every user (or a given one)... Are there any new messages?

    # If there are (for a given user; each has their own script), then:
    # call this REST API to
    # When a user makes a request
    return 0


@app.route('/api/upload', methods=['POST'])
def upload():
    # TODO: we are trusting user input in the Python upload script.
    # TODO: store references in database for the messages.

    if request.data:
        import base64
        import os
        import time
        from app import db, models

        # Used to uniquely identify the artefact and user.
        # Convert from unicode to string
        sender = str(request.json['sender'])
        receiver = str(request.json['receiver'])

        # Upload the file to the specific users directory.
        # Each file is linked with a receiver within the database.
        # NOTE: do not care about path is its hosted on a UNIX machine.
        ufiles = "audios/" + sender

        # For when a user first publishes a file.
        if not os.path.exists(ufiles):
            os.makedirs(ufiles)

        # A UNIX timestamp is used to uniquely identify the file
        path = ufiles + "/" + str(int((time.time() + (60*60))))
        with open(path, 'wb') as f:
            # NOTE: binary is encoded to allow other parameters to also be sent.
            f.write(base64.b64decode(request.json['message']))

        message = models.Message(message=path, status="sent",
                                 sid=sender, rid=receiver)
        db.session.add(message)
        db.session.commit()

        return jsonify({'success': True}), 201
    else:
        abort(500)
