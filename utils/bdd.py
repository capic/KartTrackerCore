__author__ = 'Vincent'
from sqlalchemy import *
from bdd_base import *
import config
import unirest
from beans.track import Track
from beans.session import Session
from beans.gps_datas import GPSData
from datetime import date, datetime
import json
from utils.AlchemyEncoder import *
import utils.log as log


def update_from_central_database():
    log.log("update_from_central_database", log.LEVEL_INFO)

    response = unirest.get(config.REST_ADDRESS + 'tracks',
                           headers={"Accept": "application/json"})

    tracks_list = []
    if response.code == 200:
        for json_object in response.body:
            track = Track()
            track.from_json(json_object)

            ret = db_session.query(Track).filter(Track.id == track.id).all()
            if len(ret) == 0:
                log.log("Track doesn't exist => insert", log.LEVEL_DEBUG)
                db_session.add(track)
                db_session.commit()
            else:
                log.log("Track exists => nothing to do", log.LEVEL_DEBUG)
            tracks_list.append(track)

    return tracks_list


def send_to_central_database():
    log.log("send_to_central_database", log.LEVEL_INFO)
    ret = db_session.query(Session).join(GPSData).all()

    log.log("Number of session to send: %d" % len(ret), log.LEVEL_DEBUG)
    if len(ret) > 0:
        json_sessions = json.dumps(ret, cls=new_alchemy_encoder(False, ['Session']), check_circular=False)
        response = unirest.post(config.REST_ADDRESS + 'sessions', headers={"Accept": "application/json"}, params=json_sessions)

        if response.code != 200:
            log.log("Erreur d'insertion: %s" % response.body, log.LEVEL_ERROR)


def start_track_session(track_id):
    log.log("start_track_session", log.LEVEL_INFO)
    log.log("Track id: %d" % track_id, log.LEVEL_DEBUG)
    track_session = Session()

    qry = db_session.query(func.max(Session.id_day_session).label("max_id_day_session")).filter(
        Session.date_session == date.today()).filter(Session.track_id == track_id)
    res = qry.one()

    log.log("Already a session for this day and track ? %d" % (len(res) > 0), log.LEVEL_DEBUG)
    id_day_session = 1
    if res.max_id_day_session is not None:
        id_day_session = res.max_id_day_session + 1

    track_session.date_session = date.today()
    track_session.track_id = track_id
    track_session.name = "Session " + str(id_day_session)
    track_session.id_day_session = id_day_session
    track_session.start_time = datetime.utcnow().time()

    log.log("Insert: %s" % str(track_session), log.LEVEL_DEBUG)
    db_session.add(track_session)
    db_session.commit()

    return track_session


def end_track_session(track_session):
    log.log("end_track_session", log.LEVEL_INFO)
    # update the session with end date time
    track_session.end_date_time = datetime.utcnow().time()
    log.log("Update: %s" % str(track_session), log.LEVEL_DEBUG)
    db_session.commit()