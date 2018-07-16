# sys_admin.py
import os, sys, datetime, logging, subprocess
#import serial.tools.list_ports as port
"""File of system administrative funtions and default config settings"""
sho_logger = logging.getLogger("shongololo_logger")
DATA_HEADER = "\nCO2 (PPM), Latitude, Longitude, Altitude, Air Speed (m/s), Mode, Fixed Satellites, Available Satellites,voltage,current,level,id"
DATAFILE = "data.csv"
PERIOD = 0.5
#TODO move these hard coded settings into a config file

def close_sensors(socks):
    """CLoses sensor sockets"""
    for s in socks
        try:
            s.close()
        except:
            pass

def shutdown_monitor():
    """Just logs a message that everything has been shutdown"""
    sho_logger.info("Shutting down App")

# Functions for stand alone instance
def stop_files(files,msg):
    files[0].write(msg)
    sys.stdout.flush()
    files[0].close()
    files[1].close()

def shutdown(imets,k30s):
    for i in imets:
        i.close()
    for k in k30s:
        k.close()

def clear_log(log):
    """Remove old logfile"""
    p = subprocess.Popen("> {}".format(log), stdout=subprocess.PIPE, shell=True)

def if_mk_DIR(dir):
    """Check if a given directory is present and if not create it.  No logging done as logger may not yet exist"""

    p = subprocess.Popen("ls {}".format(dir), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    print ("ls {}".format(dir))
    if p_status !=0:
        sho_logger.info("{} directory not present creating it".format(dir))
        p = subprocess.Popen("mkdir {}".format(dir), stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        if p_status == 0:
            sho_logger.info("Created {} directory".format(dir))
            return 0
        else:
            sho_logger.error("Error creating directory {0}.  {1} {2}".format(output,err))
            return -1
    else:
        sho_logger.info("Data directory present at {}".format(dir))
        return 0

def mk_ND(new_dir):
    """
    Make a new directory with name corresponding to session number
    """
    print(new_dir)
    dt = str(datetime.datetime.today())[0:10]
    p = subprocess.Popen("ls {}".format(new_dir), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    print("Output {0} Error {1} Status {2}".format(output,err,p_status))
    num=len(str(output.decode("utf-8").split("\n")))

    ND=new_dir+dt+"CAPTURE_"+str(num).zfill(3)

    p = subprocess.Popen("mkdir -p {}".format(ND), stdout=subprocess.PIPE, shell=True)
    p_status = p.wait()
    if p_status == 0:
        sho_logger.info("Successfully created new %s", ND)
        return 0, ND+"/"
    else:
        sho_logger.error("Failed to create new directory {}".format(ND))
        return -1, ""


def set_system_time(imet_device):
    """
    Captures a date and time and sets the inputs as the system date and time.
    Minimal date entry santitisation performed
    """
    try:
        l = imet_device.readline()

    except IOError as e:
        sho_logger.error("Unable read time from Imet device: %s.  Error: %s", imet_device, e)
        return -1


    i_time= l.split(',')[5:7]
    idate=i_time[0].replace('/','')
    ihour=i_time[1]
    p = subprocess.Popen("sudo date +%Y%m%d -s {}".format(idate), stdout=subprocess.PIPE, shell=True)
    sho_logger.info("Attempt to set date to: {}".format(idate))
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status !=0:
        sho_logger.error("Failed to set system time: "+output+" "+err+" "+p_status)
        return -1
    else:
        sho_logger.info("Set system time: "+ output)
        return 0

def ini_datafile(filename):
    """
    Make this session's data directory, open it's data file, and write a header
    :param filename: The full path string you want the file to be called and located at
    :return: the file handler
    """
    with open(filename) as fd:
        fd.write(DATA_HEADER)
        sho_logger.info("Started log file")
        sys.stdout.flush()

    return  fd

def read_data(isocks, ksocks):
    """
    Do the actual work of reading for all sensors
    :param isocks: list of imet_open sockets
    :param ksocks: list of k30 open sockets
    :return: a single list of outputs from all sensors read
    """
    #TODO convert this to a threaded approach of parallel sensor reading
    try:
        latestdata = []
        for k in ksocks:
            reading = KS.read_ppm(k)
            latestdata.append(reading)

        for i in isocks:
            im_values = i.readline()
            latestdata.append(im_values)

    return latestdata