from flask import request, abort, jsonify, Response
from app import app


@app.route('/api/download', methods=['GET'])
def download():
    from app import db, models
    # All the messages sent within a conversation
    all_messages = db.session.query(models.Message).filter(
        models.Message.sid == str(request.args.get('sender')),
        models.Message.rid == str(request.args.get('receiver'))).order_by(
            models.Message.mid).all()

    num_client_msgs = int(request.args.get('latest'))
    # Compare the amount of messages the server knows with that of the client.
    if len(all_messages) > num_client_msgs:
        # All messages a sender has recorded that the receiver does not have.
        audio_files = all_messages[-(len(all_messages) - num_client_msgs):]
        import zipfile
        import io
        # Store the zip-file to memory; prevents creating/deleting local zip.
        datafile = io.BytesIO()
        # Write all the new audios to a zip in a temporary directory
        with zipfile.ZipFile(datafile, 'w') as zf:
            # NOTE: the path is critical to file storage on server and client!
            for audio_file in audio_files:
                # Pre-pending as the stored message is the path client-side.
                # Use the file name (sent timestamp) for client storage.
                zf.write(audio_file.message, audio_file.message.split("/")[-1])
        # Move read-write position to start for data streaming.
        datafile.seek(0)

        return Response(datafile,
                        mimetype='application/zip',
                        headers={'Content-Disposition':
                                 'attachment;filename=voice_messages.zip'})
    elif len(all_messages) == num_client_msgs:
        # There are no new messages (content) to return
        return '', 204
    else:
        abort(500)


@app.route('/api/upload', methods=['POST'])
def upload():
    # TODO: we are trusting user input in the Python upload script.
    # TODO: store references in database for the messages.

    if request.data:
        import base64
        import os
        from app import db, models

        # Used to uniquely identify the artefact and users.
        sender = str(request.json['sender'])
        receiver = str(request.json['receiver'])

        # Upload to a shared conversation folder by unique tokens.
        # Store in the root of the flask application.
        ufiles = "audios/" + sender + "_" + receiver

        # For when a user first publishes a file.
        if not os.path.exists(ufiles):
            os.makedirs(ufiles)

        # A UNIX timestamp is used to uniquely identify the file
        path = ufiles + "/" + str(request.json['filename'])
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


@app.route('/api/matches', methods=['GET'])
def matches():
    from app import db, models

    user = str(request.args.get('user'))
    matches = None

    # IFF the user is known, then we can query for pairs.
    # A simple mechanism to overcome malicious intent.
    # TODO: validate user input further; trust no-one, especially our users!
    if db.session.query(models.User).filter(models.User.token == user).first():
        matches = [usr.mid for usr in db.session.query(models.Pair).filter(
            models.Pair.uid == user).all()]
    return jsonify({"matches": matches}), 201
