from flask import request, abort, jsonify, Response
from app import app


@app.route('/api/download', methods=['GET'])
def download():
    # TODO: validate query parameters.
    from app import db, models
    # All messages between those in a conversation.
    # TODO: simplify query to only return messages after latest
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
            for audio_file in audio_files:
                filepath = audio_file.message
                # Use the file name (sent timestamp) for client storage.
                zf.write(filepath, filepath.split("/")[-1])
        # Move read-write position to start for data streaming.
        datafile.seek(0)

        return Response(datafile,
                        mimetype='application/zip',
                        headers={'Content-Disposition':
                                 'attachment;filename=voice_messages.zip'})


@app.route('/api/upload', methods=['POST'])
def upload():
    # TODO: we are trusting user input in the Python upload script.
    # TODO: store references in database for the messages.

    if request.data:
        import base64
        import os
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
