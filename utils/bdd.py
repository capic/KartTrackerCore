__author__ = 'Vincent'
from sqlalchemy import *
from bdd_base import *
import config
import unirest
from beans.track import Track
from beans.session import Session
from datetime import date, datetime
import json


def update_from_central_database():
    response = unirest.get(config.REST_ADDRESS + 'tracks',
                           headers={"Accept": "application/json"})

    tracks_list = []
    if response.code == 200:
        for json_object in response.body:
            track = Track()
            track.from_json(json_object)
            if db_session.query(Track).filter(Track.id == track.id).one().id is None:
                print("Track doesn't exist => insert")
                db_session.add(track)
                db_session.commit()
            else:
                print("Track exists => nothing to do")
            tracks_list.append(track)

    return tracks_list


def send_to_central_database():
    ret = db_session.query(Session).all()
    print("RET : " + ret)
    j = json.dumps(ret)
    print("JSON " + j)
    unirest.post(config.REST_ADDRESS + 'sessions', headers={"Accept": "application/json"}, params=j)


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