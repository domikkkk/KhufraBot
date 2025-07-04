import socket
import struct


MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class Multicast:
    def __init__(self):
        self._multicast_ip = MCAST_GRP
        self._multicast_port = MCAST_PORT
        self.local_ip = get_local_ip()

    def udp_discovery(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self._multicast_port))

        mreq = struct.pack("4sl", socket.inet_aton(self._multicast_ip), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        return sock

        