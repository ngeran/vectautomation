# /home/nikos/github/ngeran/vectautomation/scripts/connect_to_hosts.py
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from typing import List
import logging

# Custom filter to suppress unwanted ncclient logs
class SuppressNcclientFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        # Allow only specific INFO logs
        return (
            'Connected (version' in msg or
            'Authentication (password) successful' in msg or
            record.levelno > logging.INFO  # Allow WARNING, ERROR, etc.
        )

# Configure ncclient loggers
for logger_name in ['ncclient.transport.ssh', 'ncclient.operations.rpc']:
    ncclient_logger = logging.getLogger(logger_name)
    ncclient_logger.addFilter(SuppressNcclientFilter())

def connect_to_hosts(username: str, password: str, host_ips: List[str]) -> List[Device]:
    """Connect to all Junos hosts listed in the provided list of host IPs."""
    connections = []
    try:
        for host_ip in host_ips:
            try:
                dev = Device(
                    host=host_ip,
                    user=username,
                    password=password,
                    port=22,
                    timeout=10
                )
                dev.open()
                print(f"Connected to {host_ip}")
                connections.append(dev)
            except ConnectError as error:
                print(f"Failed to connect to {host_ip}: {error} (connection issue)")
            except Exception as error:
                print(f"Failed to connect to {host_ip}: {error} (unexpected error)")
        return connections
    except KeyboardInterrupt:
        print("Connection attempt interrupted by user.")
        disconnect_from_hosts(connections)
        return []

def disconnect_from_hosts(connections: List[Device]):
    """Close all connections to the hosts."""
    for dev in connections:
        try:
            dev.close()
            print(f"Disconnected from {dev.hostname} ({dev._hostname})")
        except Exception as e:
            print(f"Error disconnecting from {dev._hostname}: {e}")
