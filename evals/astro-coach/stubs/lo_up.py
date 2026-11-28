"""Bring up the loopback interface in the current network namespace (no `ip` tool needed)."""
import fcntl
import socket
import struct

SIOCGIFFLAGS, SIOCSIFFLAGS, IFF_UP = 0x8913, 0x8914, 0x1
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
req = bytearray(40)
req[:3] = b"lo\0"
fcntl.ioctl(sock, SIOCGIFFLAGS, req)
flags = struct.unpack_from("H", req, 16)[0] | IFF_UP
struct.pack_into("H", req, 16, flags)
fcntl.ioctl(sock, SIOCSIFFLAGS, req)
