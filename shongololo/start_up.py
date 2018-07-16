# start_up.py
import getpass, logging, subprocess, time

import shongololo.sys_admin as SA
import shongololo.K30_serial as KS
import shongololo.Imet_serial as IS
user=getpass.getuser()
DATADIR = "/home/"+user+"/DATA/"

def start_up(flask_handler=None):
    """ Perform startup functions
    Optionally accepts a flask socket handler for when being used by a flask web interface
    :returns
    2 lists of open serial sockets to first imet and then k30 sensors
    """
    SA.if_mk_DIR(DATADIR)
    imets_sockets = []    # type: List of open serial sockets to Imet Sensors
    k30_sockets = []      # type: List of open serial sockets to K30 sensors

    logfile = DATADIR+"shongololo_log.log"
    SA.clear_log(logfile)
    # TODO capture_duration of run =

    # Setup Application Logging
    sho_logger = logging.getLogger("shongololo_logger")
    sho_logger.setLevel(logging.DEBUG)
    sho_fh = logging.FileHandler(logfile)
    sho_fh.setLevel(logging.DEBUG)
    sho_fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d"))

    if flask_handler!=None:
        sho_logger.addHandler(sho_fh)
        sho_logger.addHandler(flask_handler)
        sho_logger.info("Started logging")

    ## Elevate access to devices
    p = subprocess.Popen("sudo chmod +644 /dev/ttyUSB*", stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    sho_logger.info("Attempted to open permissions on devices with result:")
    if p_status==0:
        sho_logger.info("Successfully elevated permissions access on devices:" + output.decode("utf-8"))
    else:
        sho_logger.error("Failed to elevate permissions access on devices:" + output.decode("utf-8"))

    # Connect to imets 1st so can set system time and create data directory
    imet_dict = IS.find_imets(i)
    imets_sockets = IS.open_imets(imet_dict)

    # If imets present try setting system time to UTC

    if len(imets_sockets) != 0:
        SA.set_system_time(imets_sockets[0])
    else:   # Don't bother trying to get and set time from Imet
        p = subprocess.Popen("date", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        sho_logger.error("Due to no Imet devices present system time and consequently data time stamps will be based current system time: {0} {1}".format(output.decode("utf-8"),p_status))

    # Connect to CO2 meters
    k30_sockets = KS.openK30s()

    return imets_sockets, k30_sockets

def test_sensors(i_sockets, k_sockets):
    """Trying reading data from sensors"""
    sho_logger = logging.getLogger("shongololo_logger")
    sho_logger.info("Attempting to read from all sensors.")
    for k,id in zip(k_sockets,range(len(k_sockets))):
        ppm = KS.read_ppm(k)
        sho_logger.info("K30_sensor_{0}: CO2: {1}ppm".format(id,ppm))

    for i,id in zip(i_sockets,range(len(i_sockets))):
        try:
            im_values = i.readline()
            sho_logger.info("Imet_sensor_{0}: Values: {1}".format(id,im_values))
        except IOError as e:
            sho_logger.error("Unable read time from Imet device: {0}.  Error: {1}".format(i, e))
    time.sleep(0.5)

    sho_logger.info("Finished sensor test sequence")
    return 0

def packdata(list_data):
    """Takes in a list of a cycle of sampling and returns a json representation"""
    pass
#    d["sample"]={"timestamp":datetime.datetime.now().isoformat(),'k30':{'ID':1,'co2':400},'imet':{'ID':1,'Alt':20}}


