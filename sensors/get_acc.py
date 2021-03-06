from lib.mma8451 import MMA8451
import datetime
import constants
from sys import exit


def getAcc(pod_data, sql_wrapper, logging):
    logging.debug("Started getting acc data")
    acc = MMA8451()

    # read acc data
    axes = acc.get_axes_measurement()
    if axes['z'] < .9:
        logging.debug("BAD ACCELEROMETER POSITIONING, MAKE SURE Z IS DOWN AND THE ACC IS FLAT")
        # TODO: Maybe throw a fault state
    while True:
        axes = acc.get_axes_measurement()
        pod_data.acceleration.x_g = axes['x']
        pod_data.acceleration.y_g = axes['y']
        pod_data.acceleration.z_g = axes['z']

        pod_data.acceleration.moving_y_average = .5 * pod_data.acceleration.moving_y_average + .5 * pod_data.acceleration.y_g
        logging.debug(axes)
        logging.debug("Moving y average is " + str(pod_data.acceleration.moving_y_average))

        sql_wrapper.execute("INSERT INTO acc VALUES (NULL,%s,%s,%s,%s)", (datetime.datetime.now().strftime(constants.TIME_FORMAT), axes['x'], axes['y'], axes['z']))

        ##VERY IMPORTANT
        ##THIS IS THE G FORCES WE EXPECT TO DETECT WHEN MOVING TO COAST
        ##COAST CONTROLS NOTHING FOR NOW	if pod is being pushed
        # if(accData1.moving_y_average<0 and podData.state==3):
        # set pod to coast
        # 		podData.state = 4
