__author__ = 'Vincent'
from utils.bdd import *
from beans.session import Session
from datetime import datetime, date
import netifaces


def start_track_session(track_id):
    track_session = Session()

    qry = db_session.query(func.max(Session.id_day_session).label("max_id_day_session")).filter(
        Session.date_session == date.today()).filter(Session.track_id == track_id)
    res = qry.one()

    id_day_session = 1
    if res.max_id_day_session is not None:
        id_day_session = res.max_id_day_session + 1

    track_session.date_session = date.today()
    track_session.track_id = track_id
    track_session.name = "Session " + str(id_day_session)
    track_session.id_day_session = id_day_session
    track_session.start_time = datetime.utcnow().time()

    print("Insert: " + str(track_session))
    db_session.add(track_session)
    db_session.commit()

    return track_session


def end_track_session(track_session):
    # update the session with end date time
    track_session.end_date_time = datetime.utcnow().time()
    print("Update: " + str(track_session))
    db_session.commit()


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr
