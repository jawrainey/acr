from app import db


class User(db.Model):
    """
    Stores citizen/researcher details of to use when posting the artefact.
    """
    __tablename__ = 'users'

    # TODO: This token should be automatically generated via OAuth
    # NOTE: the token is the unique identifier of each artefact.
    # Generated client-side to prevent malicious intent.
    token = db.Column(db.String, primary_key=True)
    role = db.Column(db.String)
    forename = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String)
    age = db.Column(db.Integer)
    # Only ever read by developers to send artefact; free-form is fine.
    address = db.Column(db.String)


class Message(db.Model):
    """
    Stores meta-data of messages sent between citizens and researchers.
    Note: a user can send messages to several other users.
    """
    __tablename__ = 'messages'

    mid = db.Column(db.Integer, primary_key=True)  # Simpler: <sid + rid> as PK
    message = db.Column(db.String)  # The path to the audio message on server.
    status = db.Column(db.String)  # Used to differentiate sent/received.
    # NOTE: each client therefore needs the token of their partners.
    sid = db.Column(db.String, db.ForeignKey('users.token'))
    rid = db.Column(db.String, db.ForeignKey('users.token'))
    # Define relations to facilitate filters of message by a given user.
    sender = db.relationship('User', foreign_keys=sid)
    receiver = db.relationship('User', foreign_keys=rid)


class Pair(db.Model):
    """
    Records paired citizens and researchers.
    NOTE: used to see pairs and distinguish available pairs
    """
    __tablename__ = 'pairs'

    # Compound PK: tokens are unique for each pi (user) that is shipped.
    uid = db.Column(db.String, db.ForeignKey('users.token'), primary_key=True)
    mid = db.Column(db.String, db.ForeignKey('users.token'), primary_key=True)
    # TODO: prevent references to same user: ForeignKeyConstraint?
    user = db.relationship('User', foreign_keys=uid)
    match = db.relationship('User', foreign_keys=mid)


class Skill(db.Model):
    """
    Unique store of skills; defined by users, but not restricted to that.
    """
    __tablename__ = 'skills'

    sid = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String, unique=True)


class UserSkills(db.Model):
    """
    Stores references to all skills defined by a user through normalisation.
    """
    __tablename__ = 'userSkills'

    uid = db.Column(db.String, db.ForeignKey('users.token'), primary_key=True)
    sid = db.Column(db.String, db.ForeignKey('skills.sid'), primary_key=True)
    # Relation: a user can have many skills, including those defined by others.
    user = db.relationship('User', foreign_keys=uid)
    skill = db.relationship('Skill', foreign_keys=sid)
