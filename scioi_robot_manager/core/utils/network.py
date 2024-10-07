import socket
import os
import subprocess
import sys
from utils.logging import Logger

logger = Logger('network')


def getIP():
    """

    :param debug:
    :return:
    """

    local_ip = None
    usb_ip = None

    if os.name == 'nt':

        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.0")]

        if len(local_ips) == 0:
            return None

        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.0")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    elif os.name == 'posix':
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]
        local_ips = [ip for ip in ip_addresses if ip.startswith("192.168.")]
        if len(local_ips) == 0:
            return None
        local_ip = [ip for ip in ip_addresses if ip.startswith("192.168.")][:1][0]
        usb_ip = ''
        server_address = socket.gethostbyname_ex(socket.gethostname())

    output = {'hostname': hostname, 'local': local_ip, 'usb': usb_ip, 'all': server_address[2]}
    logger.debug(f"\tHostname: {socket.gethostname()}")
    logger.debug(f"\tLocal: {local_ip}")
    logger.debug(f"\tUSB: {usb_ip}")
    for i, add in enumerate(server_address[2]):
        if add is not local_ip and add is not usb_ip:
            logger.debug(f"\tIP {i}: {add}")

    logger.debug('\t-------------'
                  '')
    return output
