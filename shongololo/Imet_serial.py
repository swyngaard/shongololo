import serial , time , os
import serial.tools.list_ports as port
import logging
sho_logger = logging.getLogger("shongololo_logger")




def open_imets(devices):
    """Tries to open as many imet device serial ports as there are
    :return:
     a list of socket handles
    """
    imet_sockets = []
    for d in range(len(devices)):  # Create list of imet open ports
        port = str(devices["Imet" + str(d)])
        try:
            ser = serial.Serial(port, baudrate=57600, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS,stopbits=serial.STOPBITS_ONE, timeout=3.0, xonxoff=False)
            imet_sockets.append(ser)
            sho_logger.info("\n Successfully opened Imet device on port {}".format(devices["Imet" + str(d)]))

        except serial.SerialException as e:
            sho_logger.error(e)
            sho_logger.critical("\nFailed to open imet on port {}".format(devices["Imet" + str(d)]))

     return imet_sockets


def find_imets():
    """
    Finds available imet serial ports and determines which device is attached to which /dev/ path
    :rtype: object
    :return:
    A dictionary of devices labled as" imet<number starting from 0>
    """
    device_dict = {}
    imets = 0
    portlist = list(port.comports())
    for p in portlist:
        sp = str(p)
        if "FT230" in sp:
            path = sp.split('-')[0]
            device_dict["Imet" + str(imets)] = path[:-1]
            imets = imets + 1
            sho_logger.info("Found an Imet device on port: %s",path)
            status=0
        else:
           pass
    if imets==0:
        sho_logger.error("No Imet devices found.")
    else:
        sho_logger.info("Found {} Imet devices".format(imets))

    return device_dict
