__author__ = 'Vincent'
from sqlalchemy import *
from bdd_base import *
import config
import unirest
from datetime import date, datetime
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

    log.log("Tracks treatment...", log.LEVEL_INFO)
    ret = db_session.query(Track).filter(Track.new == True).all()
    log.log("Numer of tracks to send: %d" % len(ret), log.LEVEL_DEBUG)
    if len(ret) > 0:
        json_tracks = json_dumps(ret, cls=new_alchemy_encoder(False, []), check_circular=False)
        unirest.timeout(99999)
        param = {"datas": json_tracks}
        response = unirest.post(config.REST_ADDRESS + 'tracks/list', headers={"Accept": "application/json"}, params=param)

        if response.code != 200:
            log.log("Erreur d'insertion: %s" % response.body, log.LEVEL_ERROR)
        else:
            log.log("Tracks ids inserted: %s" % response.body, log.LEVEL_DEBUG)
            log.log("Update 'new' flags to false for tracks inserted", log.LEVEL_INFO)
            for track in ret:
                for id_json in response.body:
                    if track.id == id_json.id:
                        log.log("Track found => delete %s" % track, log.LEVEL_DEBUG)
                        track.new = False
                        db_session.update(track)
                        break

    log.log("Sessions treatment...", log.LEVEL_INFO)
    ret = db_session.query(Session).all()
    log.log("Number of session to send: %d" % len(ret), log.LEVEL_DEBUG)
    if len(ret) > 0:
        json_sessions = json.dumps(ret, cls=new_alchemy_encoder(False, ['gps_datas']), check_circular=False)
        unirest.timeout(99999)
        param = {"datas": json_sessions}
        response = unirest.post(config.REST_ADDRESS + 'sessions/list', headers={"Accept": "application/json"}, params=param)

        if response.code != 200:
            log.log("Erreur d'insertion: %s" % response.body, log.LEVEL_ERROR)
        else:
            log.log("Session ids inserted: %s" % response.body, log.LEVEL_DEBUG)
            log.log("Delete sessions inserted", log.LEVEL_INFO)
            for session_json in ret:
                session = Session()
                session.from_json(session_json)
                db_session.delete(session)
                break


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