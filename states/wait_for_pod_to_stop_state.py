import datetime
import MySQLdb
import logging
import time
import constants


def _check_pod_is_stopped(pod_data):
    time.sleep(1)
    if pod_data.acceleration.y_g < 0.1:
        return True
    return False


def start(pod_data, sql_wrapper, drive_controller):
    try:
        sql_wrapper.execute("""INSERT INTO states VALUES ( %s,%s)""", (datetime.datetime.now(), "WAITING FOR POD TO STOP"))
    except MySQLdb.OperationalError, e:
        # Ignore error because we need to keep braking
        logging.error(e)

    while True:
        # be VERY sure that we're stopped
        if pod_data.acceleration.y_g < 0.1:
            first_try = _check_pod_is_stopped(pod_data)
            second_try = _check_pod_is_stopped(pod_data)
            third_try = _check_pod_is_stopped(pod_data)
            if first_try and second_try and third_try:
                break

    try:
        sql_wrapper.execute("""INSERT INTO states VALUES ( %s,%s)""", (datetime.datetime.now(), "POD IS STOPPED"))
    except MySQLdb.OperationalError, e:
        # Ignore error because we need to keep braking
        logging.error(e)

    drive_controller.send_stopped()

    while drive_controller.get_response() != constants.STOPPED:
        drive_controller.send_stopped()
        time.sleep(.1)