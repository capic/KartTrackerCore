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

    log.log("[=== Tracks treatment ===]", log.LEVEL_INFO)
    ret = db_session.query(Track).filter(Track.new == True).all()
    log.log("==> Number of tracks to send: %d" % len(ret), log.LEVEL_DEBUG)
    if len(ret) > 0:
        json_tracks = json.dumps(ret, cls=new_alchemy_encoder(False, []), check_circular=False)
        unirest.timeout(99999)
        param = {"datas": json_tracks}
        response = unirest.post(config.REST_ADDRESS + 'tracks/list', headers={"Accept": "application/json"},
                                params=param)

        if response.code != 200:
            log.log("Insertion error: %s" % response.body, log.LEVEL_ERROR)
        else:
            log.log("Update 'new' flags to false for tracks inserted", log.LEVEL_INFO)
            for track in ret:
                log.log("Update track id: %d" % track.id, log.LEVEL_DEBUG)
                track.new = False
                db_session.update(track)
                db_session.commit()
    else:
        log.log("No track to insert", log.LEVEL_INFO)

    log.log("[=== Sessions treatment ===]", log.LEVEL_INFO)
    ret = db_session.query(Session).all()
    log.log("%s" % ret, log.LEVEL_DEBUG)
    log.log("==> Number of session to send: %d" % len(ret), log.LEVEL_INFO)
    if len(ret) > 0:

        for session in ret:
            json_sessions_only = json.dumps(session, cls=new_alchemy_encoder(False, []), check_circular=False)
            log.log("JSON session: %s" % json_sessions_only, log.LEVEL_DEBUG)
            param = {"datas": json_sessions_only}
            log.log("===> Insert session: %d" % session.id, log.LEVEL_INFO)
            response = unirest.post(config.REST_ADDRESS + 'sessions', headers={"Accept": "application/json"},
                                    params=param)

            if response.code == 200:
                log.log("Session inserted successfully", log.LEVEL_INFO)
                log.log("==> Number of gps datas to send: %d" % len(session.gps_datas), log.LEVEL_INFO)
                i = 0
                error = False
                while i < len(session.gps_datas) and not error:
                    gps_data = session.gps_datas[i]
                    json_gps_data = json.dumps(gps_data, cls=new_alchemy_encoder(False, []), check_circular=False)
                    log.log("JSON session: %s" % json_gps_data, log.LEVEL_debug)
                    param = {"datas": json_gps_data}
                    log.log("====> Insert gps data: %d" % gps_data.id, log.LEVEL_INFO)
                    response = unirest.post(config.REST_ADDRESS + 'gpsdatas', headers={"Accept": "application/json"},
                                            params=param)

                    if response.code != 200:
                        log.log("!!! Error insertion !!!", log.LEVEL_ERROR)
                        error = True
                    else:
                        log.log("GPS datas inserted successfully", log.LEVEL_INFO)

                    i += 1

                if not error:
                    i = 0
                    while i < len(session.accelerometer_datas) and not error:
                        accelerometer_data = session.accelerometer_datas[i]
                        json_accelerometer_data = json.dumps(accelerometer_data, cls=new_alchemy_encoder(False, []), check_circular=False)
                        param = {"datas": json_accelerometer_data}
                        log.log("====> Insert accelerometer data: %d" % accelerometer_data.id, log.LEVEL_INFO)
                        response = unirest.post(config.REST_ADDRESS + 'accelerometerdatas',
                                                headers={"Accept": "application/json"},
                                                params=param)

                        if response.code != 200:
                            log.log("!!! Error insertion !!!", log.LEVEL_ERROR)
                            error = True
                        else:
                            log.log("Accelerometer datas inserted successfully", log.LEVEL_INFO)

                        i += 1

                if error:
                    log.log("There are errors during sessions data insertion => delete session %d" % session.id, log.LEVEL_DEBUG)
                    unirest.delete(config.REST_ADDRESS + 'session/' + session.id,
                                                headers={"Accept": "application/json"})
                else:
                    log.log("Delete session", log.LEVEL_INFO)
                    db_session.delete(session)
                    db_session.commit()
    else:
        log.log("No session to insert", log.LEVEL_INFO)


def start_track_session(track_id):
    log.log("start_track_session", log.LEVEL_INFO)
    log.log("Track id: %d" % track_id, log.LEVEL_DEBUG)
    track_session = Session()

    try:
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
    except Exception:
        raise

    return track_session


def end_track_session(track_session):
    log.log("end_track_session", log.LEVEL_INFO)
    # update the session with end date time
    track_session.end_time = datetime.utcnow().time()
    log.log("Update: %s" % str(track_session), log.LEVEL_DEBUG)
    db_session.commit()
