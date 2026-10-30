"""netcheck.py: can I reach HOST on PORT? If not, which step failed?

Usage: python3 netcheck.py HOST PORT
"""

import socket
import sys
import time


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python3 netcheck.py HOST PORT")
        return 2
    host, port = sys.argv[1], int(sys.argv[2])

    # Step 1: turn the name into an address, with the same resolver apps use
    # (/etc/hosts first, then DNS).
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror as err:
        print(f"DNS FAIL  {host} does not resolve ({err.strerror})")
        return 1
    print(f"DNS OK    {host} -> {ip}")

    # Step 2: open a TCP connection (the three-way handshake).
    start = time.monotonic()
    try:
        with socket.create_connection((ip, port), timeout=3):
            ms = (time.monotonic() - start) * 1000
            print(f"TCP OK    {ip}:{port} accepted the connection in {ms:.0f} ms")
            return 0
    except ConnectionRefusedError:
        print(f"REFUSED   {ip}:{port} answered, but no program listens on that port")
    except TimeoutError:
        print(f"TIMEOUT   {ip}:{port} sent no answer in 3 s (dropped by a firewall, or a wrong address)")
    except OSError as err:
        print(f"ERROR     {ip}:{port} {err.strerror}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
