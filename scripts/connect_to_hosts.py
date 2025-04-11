# /home/nikos/Development/scripts/connect_to_hosts.py
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from typing import List

def connect_to_hosts(username: str, password: str, host_ips: List[str]) -> List[Device]:
    """Connect to all Junos hosts listed in the provided list of host IPs.

    Args:
        username (str): SSH username for device authentication.
        password (str): SSH password for device authentication.
        host_ips (list): List of host IPs to connect to.

    Returns:
        list: List of PyEZ Device objects for successfully connected hosts.
    """
    connections = []
    for host_ip in host_ips:
        try:
            dev = Device(
                host=host_ip,
                user=username,
                password=password,
                port=22,
                timeout=10  # Add timeout to avoid hanging
            )
            dev.open()
            print(f"Connected to {host_ip}")
            connections.append(dev)
        except ConnectError as error:
            print(f"Failed to connect to {host_ip}: {error} (connection issue)")
        except Exception as error:
            print(f"Failed to connect to {host_ip}: {error} (unexpected error)")
    return connections

def disconnect_from_hosts(connections: List[Device]):
    """Close all connections to the hosts.

    Args:
        connections (list): List of PyEZ Device objects to disconnect.
    """
    for dev in connections:
        try:
            dev.close()
            print(f"Disconnected from {dev.hostname} ({dev._hostname})")
        except Exception as e:
            print(f"Error disconnecting from {dev._hostname}: {e}")

if __name__ == "__main__":
    # Test with sample data
    test_ips = ["172.27.200.200", "172.27.200.201"]
    connections = connect_to_hosts(username="admin", password="manolis1", host_ips=test_ips)
    disconnect_from_hosts(connections)
