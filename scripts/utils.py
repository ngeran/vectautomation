# /home/nikos/Development/scripts/utils.py
import os
import yaml

def load_yaml_file(file_path):
    """
    Load a YAML file and return its contents as a Python dict or list.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict or list: Parsed YAML data, or None if loading fails.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except yaml.YAMLError as error:
        print(f"Error parsing YAML file {file_path}: {error}")
        return None
    except Exception as error:
        print(f"Unexpected error loading {file_path}: {error}")
        return None

def flatten_inventory(inventory):
    """
    Flatten inventory.yml into a list of hosts from switches, routers, and firewalls.

    Args:
        inventory (list): Parsed inventory.yml data (list of location dicts).

    Returns:
        list: Flat list of host dicts.
    """
    flat_hosts = []
    for location in inventory:
        for category in ['switches', 'routers', 'firewalls']:
            if category in location:
                for host in location[category]:
                    # Add location to host data for reference
                    host['location'] = location['location']
                    flat_hosts.append(host)
    return flat_hosts

def merge_host_data(inventory_file, hosts_data_file):
    """
    Merge data from inventory.yml and hosts_data.yml, matching hosts by IP or hostname.

    Args:
        inventory_file (str): Path to inventory.yml (list of location dicts).
        hosts_data_file (str): Path to hosts_data.yml (dict with 'hosts').

    Returns:
        dict: Merged data with credentials, tables, and enriched host list, or None if failed.
    """
    # Load both files
    inventory = load_yaml_file(inventory_file)
    hosts_data = load_yaml_file(hosts_data_file)

    if not inventory or not hosts_data:
        return None

    # Extract top-level fields from hosts_data
    merged = {
        'username': hosts_data.get('username', 'admin'),
        'password': hosts_data.get('password', ''),
        'interval': hosts_data.get('interval', 300),
        'tables': hosts_data.get('tables', ['inet.0'])
    }

    # Flatten inventory into a list of hosts
    inventory_hosts = flatten_inventory(inventory)
    inventory_lookup = {host['ip_address']: host for host in inventory_hosts}

    # Merge hosts from hosts_data with inventory
    merged_hosts = []
    for host in hosts_data.get('hosts', []):
        ip = host.get('ip_address')
        if ip in inventory_lookup:
            # Merge inventory data (e.g., vendor, platform) with hosts_data (e.g., interfaces)
            merged_host = inventory_lookup[ip].copy()
            merged_host.update(host)
            merged_hosts.append(merged_host)
        else:
            # Warn if host isn’t in inventory, but include it
            print(f"Warning: Host '{host.get('host_name', ip)}' in hosts_data.yml not found in inventory.yml")
            merged_hosts.append(host)

    # Check for inventory hosts not in hosts_data
    for ip, inv_host in inventory_lookup.items():
        if not any(h['ip_address'] == ip for h in merged_hosts):
            print(f"Warning: Host '{inv_host['host_name']}' in inventory.yml not found in hosts_data.yml")
            merged_hosts.append(inv_host)

    merged['hosts'] = merged_hosts
    return merged

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    inventory_file = os.path.join(SCRIPT_DIR, "../data/inventory.yml")
    hosts_data_file = os.path.join(SCRIPT_DIR, "../data/hosts_data.yml")
    data = merge_host_data(inventory_file, hosts_data_file)
    if data:
        print("Merged data:", data)
