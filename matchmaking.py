def matchmaking():
    """
    Matches un-matched users based on skills.

    NOTE: this algorithm is a proof of concept with a lesser focus (though
    important) and is therefore simple with suggested improvements below:

    Returns:

        (email): emails the participants that they have been matched,
         and will receive an item in the future.
    """
    from app import db, models
    # Split by character as they are stored as a list in the database.
    # Could improve by normalising skills & model already produced -- models::skills
    # Query would change below, but matchmaking algorithm would remain the same.
    uskills = [{'name': str(i.uid), 'skills':
                [str(i) for i in i.skills.split(",")]}
               for i in db.session.query(models.UserSkills).all()]
    # Used to select matches that have not been previously paired.
    pairs = [(str(i.uid), str(i.mid))
             for i in db.session.query(models.Pair).all()]

    # Find all the users who are not already matched, but should be!
    # IFF at least once skill overlaps then there is a match. We are too kind.
    matches = []
    for user in uskills:
        for other_user in uskills:
            # Do not add already existing pairs and matches are transitive;
            # Jay matched with Aare is the same as Aare matching with Jay.
            cu, ou = (user['name'], other_user['name'])
            if ((cu, ou) in pairs or (ou, cu) in pairs or
                (cu, ou) in matches or (ou, cu) in matches):
                    break
            # TODO: skill comparison based on NLTK use (synonyms, etc...)
            # TODO: improve the algorithm to rank and sort pairs by skills.
            if (set(user['skills']).intersection(other_user['skills']) and
                    user['name'] != other_user['name']):
                matches.append((user['name'], other_user['name']))
    return matches

if __name__ == '__main__':
    # TODO: run this nightly to match new users
    # TODO: when users have been matched, they should be emailed.
    matchmaking()
