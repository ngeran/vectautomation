import os
import argparse
from utils import merge_host_data

# Define the script directory for consistent file paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    """Parse commend-line arguments and execute specified actions"""
    #Set up argument parser
    parser = argparse.ArgumentParser(description="Network device automation tool")
    parser.add_argument('--actions', nargs='+',
                        choices=['interfaces', 'bgp', 'ospf', 'ldp', 'rsvp', 'mpls',
                                 'ping', 'bgp_verification', 'ospf_verification',
                                 'backup', 'baseline', 'route_monitor'],
                        help="Actions to perform (e.g., 'ping', 'backup')")
    args = parser.parse_args()

    # Define file paths
    inventory_file = os.path.join(SCRIPT_DIR, "../data/inventory.yml")
    hosts_data_file = os.path.join(SCRIPT_DIR, "../data/hosts_data.yml")

    # Load and merge data
    merged_data = merge_host_data(inventory_file,hosts_data_file)
    if not merged_data:
        print("Failed to load or merge data. Exiting.")
        return

    # Extract common fields
    username = merged_data['username']
    password = merged_data['password']
    hosts = merged_data['hosts']
    host_ips = [host['ip_address'] for host in hosts]
    interval = merged_data['interval']

    # Placeholder for actions (to be filled as we rebuild)
    if not args.actions:
        print("No actions specified. Use --actions with one or more of:", parser.parse_args(['--help']).actions)
        return

    print(f"Loaded {len(hosts)} hosts. Actions to perform: {args.actions}")
    # We’ll add action imports and calls in later steps

if __name__ == "__main__":
    main()
