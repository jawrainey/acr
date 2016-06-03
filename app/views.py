from flask import redirect, request, render_template
from app import app, db, forms, models


@app.route('/', methods=['GET'])
def index():
    """
    A description of the project and how to get involved.
    """
    return render_template('index.html')


@app.route('/participate', methods=['GET', 'POST'])
def participate():
    """
    Provides a form for a researcher or citizen to sign-up to our service.
    """
    # TODO: De-couple validation from views through server-side validation
    # by using WTForms. Opted not to do this due to time constraints.
    if request.method == "POST":
        # TODO: we trust our users input... Ohhhh my -- George Takei
        import hashlib
        import uuid
        # TODO: using sha256 is extremely insecure, though
        # demonstrates the idea behind using a unique token.
        name = request.form['forename'] + request.form['surname']
        token = hashlib.sha256(uuid.uuid4().hex + name).hexdigest()
        # All is well; let's add a new user and their skills to our system!
        nuser = models.User(token=token,
                            role=request.form['role'],
                            name=name,
                            email=request.form['email'],
                            address=request.form['address'])
        db.session.add(nuser)
        db.session.commit()
        # Add skills separately, though link them to this specific user.
        us = models.UserSkills(uid=token, skills=request.form['skills'])
        db.session.add(us)
        db.session.commit()
        # TODO: flash a message to the user to say all went well!
        return redirect('/')
    return render_template('form.html')