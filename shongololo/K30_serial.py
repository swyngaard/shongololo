import time, logging, serial
import serial.tools.list_ports as port
sho_logger = logging.getLogger("shongololo_logger")

def read_ppm(socket):
    """ Read data from a CO2 meter and return both the scaled result in ppm and a time stamp from when the reading was receieved
        stream = socket
        returns tuple of strings: time stamp, CO2 ppm value
    """
    socket.write("\xFE\x44\x00\x08\x02\x9F\x25")
    time.sleep(.5)
    resp = socket.read(7)
    try:
        high = ord(resp[3])
        low = ord(resp[4])
        co2 = (high * 256) + low

    except IndexError as e:
        e = sys.exc_info()
        sho_logger.error="Unexpected errors reading from socket{0} \n Error: {1}".format(socket, e)
        return

    return str(co2)

def find_k30s():
    """
    Finds available k30 serial ports and determines which device is attached to which /dev/ path
    :return:
    A dictionary of devices labled as" K30<number starting from 0>
    """
    device_dict = {}
    k30s = 0
    portlist = list(port.comports())
    for p in portlist:
        sp = str(p)
        if "CP2102" in sp:
            path = sp.split('-')[0]
            device_dict["K30" + str(k30s)] = path[:-1]

            sho_logger.info("Discovered K30 port {0} on: {1} ".fomat(K30s,p))
            k30s = k30s + 1

        else:
            pass
    if k30s == 0:
        sho_logger.error("No K30 devices found")
    else:
        sho_logger.info("Found {} K30 devices".format(k30s))
    return device_dict

def open_k30s(devices):
    """ Tries to open as many K30 device serial ports as there are
        Returns: a list of socket handles
    """
    k30_sockets = []
    for d in range(len(devices)):
        port = str(devices["K30" + str(d)])
        try:
            ser = serial.Serial(port, baudrate=9600, timeout=.5)
            k30_sockets.append(ser)
            sho_logger.info("Succesfully opened K30 on port {}".format(devices["K30" + str(d)]))
        except serial.SerialException as e:
            sho_logger.error(e)
            sho_logger.error("Failed to open k30 on port {}".format(devices["K30" + str(d)]))

    return k30_sockets

