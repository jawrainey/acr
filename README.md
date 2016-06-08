# Active Citizen Research (ACR)

> How can technologies enable citizens to have an active role in research?

This project aims to explore this question through the design of two hardware
prototypes and accompanying software, which is split into three software components:

1. __Server:__ website to acquire new participants using their perceived or desired skills
for comparative analysis and matchmaking.
2. __Server:__ REST web service to mediate and store messages between users.
3. __Client:__ bespoke software for direct audio communication between prototypes.

The technology design choices were directed from a previous workshop held with three
citizens and researchers that explored the potential of technologies to broker a
citizen's local community knowledge and skills to further an area of research to them.

## Features

The core features of the client are assigned to an individual button on each artefact:

- __record:__ record an audio and send it to the current matched user
- __play:__ plays an audio message for the current matched user.
- __next:__ plays the next audio message in a conversation.
- __previous:__ plays the previous audio message from a matched user.
- __users:__ switches between matched users if there are matches. All other features
reflect this change, e.g. play will play for the current matched user.
- __notify:__ flashes LEDs to notify the user of a change: matched users, recording
audio, and message sent.

__Note:__ once `client.py` is run, it will check every 5 minutes for new messages and matches.

The server hosts the website for participants to get involved (i.e. sign-up), and the
REST web service used by the client codebase:

- __Website:__ responsive, mobile first website to recruit new participants.
- __Matchmaking:__ proof-of-concept algorithm that matches citizens to researchers based
on the citizen's skills and the researchers desired skills for a project.
- __REST API:__ enables a client to obtain messages for a given conversation and new matches.
    - __upload:__ enables a user to send another user an audio message.
    - __download:__ enables a user to download all unread audio messages in a conversation.
    - __matches:__ finds all the matched users for a given user.

### Technologies used

- [Server codebase](https://github.com/jawrainey/jar/tree/master/app)
    - [Python Flask](http://flask.pocoo.org/) framework to power the back-end
    - [Flask-SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/) for storage and
    [ORM](https://github.com/jawrainey/jar/blob/master/app/models.py) to simplify database access
    - [Requests](http://docs.python-requests.org/en/master/) to create a REST service for audio access and transmission
    - [Bootstrap Freelancer](https://github.com/BlackrockDigital/startbootstrap-freelancer)
heavily modified theme for sign-up website

- [Client codebase](https://github.com/jawrainey/jar/tree/master/client)
    - [RPIO](https://github.com/metachris/RPIO) to invoke Python methods when
    specific buttons have been pressed on a raspberry Pi
    - [Requests](http://docs.python-requests.org/en/master/) to access the REST service
    - [Bespoke software](https://github.com/jawrainey/jar/tree/master/client/client.py)
    interacting with the REST service to provides core features to each PI

### Repository structure

This repository hosts the codebase for the client _(audio communication between devices)_ and
server _(REST service & website)_.

- run.py
    - Starts the web server when invoked
- matchmaking.py
    - An algorithm that is invoked nightly to match un-matched users and notify them.
- **app/**
    - **/static/**
        - The `css/javascript/images` used by the website
    - **/templates/**
        - The markup files used to create the frontend
    - \__init\__.py
        - Used to initialise the Flask application
    - api.py
        - The REST API for client interactions (upload/download/matching)
    - models.py
        - Database representation for the ORM
    - views.py
        - Delivers web-pages (templates) for given requests. Stores user details to database.
- **client/**
    - client.py
        - An independent script that provides audio communication functionality for devices
    - loader.sh
        - A shell script to run the client code upon Raspberry Pi - via a cron job.

## Installation &mdash; local development

Create a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to
install the dependencies required to run the __server__:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Note: the client codebase requires [RPIO](https://github.com/metachris/RPIO) GPIO toolbox
to be installed on the Raspberry PI machine as it is not provided as a requirement &mdash;
the server and API exist regardless of client codebase.

### Viewing the website

You can view the website locally at `http://127.0.0.1:8080/` by running the
[flask app](https://github.com/jawrainey/jar/blob/master/run.py):

    python run.py

This creates the Flask application, which the [REST API](https://github.com/jawrainey/jar/blob/master/app/api.py) is hosted.
Establishing a server is required before running the [client codebase](https://github.com/jawrainey/jar/blob/master/client/client.py).

### Running the client code

To run the client code a client must first be matched, and you must have two instances and
hardware to validate a bi-directional conversation. To ease development, `pop.py` was written
that automatically creates the database and initial message. This should be run once:

    python pop.py

The client code can now be run. By default, you would have been matched with `rem`. You can
then send messages to the matched user through your custom hardware (or our artefact).

#### Validating messages sent

Modify the `api_key` in `clients.py` to `rem` &mdash; the person you just sent messages to.
If you run the client script again you can now playback all the audio's you sent.

#### Network configuration

To make the website [externally visible](http://flask.pocoo.org/docs/0.11/quickstart/#a-minimal-application)
modify the host address in `run.py` to `0.0.0.0`, which opens the server for access on the local network
(Intranet) through the IP address of the server. You then need to __(1)__ find the IP address of the server
and __(2)__ manually update `client.py` to point to this address. To do that:

1) run `ifconfig` and make note of the `inet` of `etho0`. This is the IP
address of the machine you are running the server on.
2) update `client.py` to point to your server
3) ensure that both the _server_ and _client_ are on the same network that has port 8080 open
(this would not work on a university network, but would work at home or `OL-Kitchen-WIFI`)
