from flask import render_template


def index():
    # Landing page: what's the project about?
    # Big button to "Get involved"
    return render_template('index.html')


def involved():
    # A form that allows participants to input their skills or projects?
    # Drop-down for auto-completion
    return render_template('involved.html')


def citizen():
    # get all the data
    # store it into a database
    return render_template('citizen.html')


def __selection():
    # It's only words and words are all I have...
    # Using the citizens skills (words) & researchers desired skills (words):
    #   How best do we match a citizen to a researcher?
    # This algorithm runs NIGHTLY to kick-off the next stage -- send artefact.
    # Therefore, we should send an email to inform participants that a device
    # will be sent to them within a given timeframe?
    return 0
