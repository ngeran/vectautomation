import yaml
from typing import Dict, List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_yaml_file(file_path: str) -> Optional[Union[Dict,List]]:
    """Load a YAML file and return its contents as a Python dict or list."""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"File not found at {file_path}")
        return None
    except yaml.YAMLError as error:
        logger.error(f"Error parsing YAML file {file_path}: {error}")
        return None
    except Exception as error:
        logger.error(f"Unexpected error loading {file_path}: {error}")
        return None

def flatten_inventory(inventory: List[Dict]) -> List[Dict]:
    """Flatten inventory.yml into a list of hosts from switches, routers, and firewalls."""
    flat_hosts = [] # Empty list
    # Each item in inventory is a location dictionary
    for location in inventory:
        for category in ['switches', 'routers', 'firewalls']:
            # Checks if category exists
            if category in location:
                # Loop through hosts in category
                # All switches, routers or firewalls in that location
                for host in location[category]:
                    # Adds a new key to each host dictionary, assigning it the
                    # value for the current location
                    host['location'] = location['location']
                    # Add host to the flat list
                    # Appends the modified host dictionary
                    flat_hosts.append(host)
    return flat_hosts

def merge_host_data(inventory_file: str, hosts_data_file: str) -> Optional[Dict]:
    """Merge data from inventory.yml and hosts_data.yml, matching hosts by IP or hostname."""
    inventory = load_yaml_file(inventory_file)
    hosts_data = load_yaml_file(hosts_data_file)
    # Validate input if either file failes to load
    if not inventory or not hosts_data:
        return None

    merged = {
        'username': hosts_data.get('username', 'admin'),
        'password': hosts_data.get('password', ''),
        'interval': hosts_data.get('interval', 300),
        'tables': hosts_data.get('tables', ['inet.0'])
    }
    # Extract a flat list of hosts
    inventory_hosts = flatten_inventory(inventory)
    # Create a fast lookup dictionary, mapping ip_address -> host for quick loockup
    inventory_lookup = {host['ip_address']: host for host in inventory_hosts}
    # Create an empty list
    merged_hosts = []
    # Loop through hosts from hosts_data.yml
    for host in hosts_data.get('hosts', []):
        # Extract the IP address form the current host
        ip = host.get('ip_address')
        # Checks if the ip exists in the inventory file ( via the lookup dictionary )
        if ip in inventory_lookup:
            merged_host = inventory_lookup[ip].copy()
            merged_host.update(host)
            merged_hosts.append(merged_host)
        else:
            logger.warning(f"Host '{host.get('host_name', ip)}' in hosts_data.yml not found in inventory.yml")
            merged_hosts.append(host)
    # Loop through all inventory hosts and check if missing from merged_hosts
    for ip, inv_host in inventory_lookup.items():
        if not any(h['ip_address'] == ip for h in merged_hosts):
            #logger.warning(f"Host '{inv_host['host_name']}' in inventory.yml not found in hosts_data.yml")
            merged_hosts.append(inv_host)

    # Add the merged hosts to results
    merged['hosts'] = merged_hosts
    return merged
