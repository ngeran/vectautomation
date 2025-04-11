import os
import yaml

def load_yaml_file(file_path):
    """Load a YAML file and return the contents as a Python object."""
    # First if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    try:
        # Open and parse YAML file safely
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

def merge_host_data(inventory_file, hosts_data_file):
    # Load both files
    inventory = load_yaml_file(inventory_file)
    hosts_data = load_yaml_file(hosts_data_file)

    if not inventory or not hosts_data:
        return None
    # Extract top-level fields from the hosts_data
    merged = {
        'username': hosts_data_file.get('username', ''),
        'password': hosts_data_file.get('password', ''),
        'interval': hosts_data_file.get('interval', 300),
        'table': hosts_data_file.get('tables', ['inet.0']) # Default Routing Table
    }

    # Build a lookup for inventory hosts by IP
    inventory_lookup = {host['ip_address']: host for host in inventory.get('hosts', [])}

    # Merge hosts from hosts_data with inventory
    merged_hosts = []
    for host in hosts_data.get('hosts', []):
        ip = host.get('ip_address')
        if ip in inventory_lookup:
            # Merge inventory data (e.g, IP) with hosts_data (e.g. interfaces, protocols)
            merged_host = inventory_lookup[ip].copy()
            merged_host.update(host)
            merged_hosts.append(merged_host)
        else:
            # Warn if host is not in the inventory, but still include it
            print(f"Warning: Host '{host.get('host_name', ip)}' in hosts_data.yml not found in inventory.yml")
            merged_hosts.append(host)

    merged['hosts'] = merged_hosts
    return merged

# Example usage (for testing)
if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    inventory_file = os.path.join(SCRIPT_DIR, "../data/inventory.yml")
    hosts_data_file = os.path.join(SCRIPT_DIR, "../data/hosts_data.yml")
    data = merge_host_data(inventory_file, hosts_data_file)
    if data:
        print("Merged data:", data)
