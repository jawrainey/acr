# CRES: Citizen-RESearchers


> How can technologies mediate the relationship between citizens and researchers,
and facilitate an active role in research for citizens?

We ([Jay](https://openlab.ncl.ac.uk/people/b5060990/),
[Aare](https://openlab.ncl.ac.uk/people/b5064252/),
[Reem](https://openlab.ncl.ac.uk/people/b5017717/)) explore these questions through the design of
two bespoke hardware prototypes and accompanying software, which is split into three software components:

1. A website to acquire new participants using their perceived and desired
for comparative analysis and matchmaking.
2. A bespoke software for direct audio communication between prototypes.
3. A server and REST service to mediate and store these messages.

## Project structure

The project is written in [Python](https://www.python.org/),
using [Flask](http://flask.pocoo.org/) as the back-end (with
[SQLAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/) for storage) and a modified
[Boostrap Freelancer](https://github.com/BlackrockDigital/startbootstrap-freelancer)
as the frontend.

## Installation

Create a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to
install the dependencies required to run the system:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

### Viewing the site

You can view the website locally at `http://127.0.0.1:8080/` by running the
[flask app](https://github.com/jawrainey/jar/blob/master/run.py):

    python run.py

To make the website [externally visible](http://flask.pocoo.org/docs/0.11/quickstart/#a-minimal-application)
modify the host address to in `run.py` and `client.py` to `0.0.0.0`, which uses
the machines IP address it is running to host the website.