# /home/nikos/github/ngeran/vectautomation/main.py
import os
import argparse
from scripts.utils import merge_host_data
from scripts.connect_to_hosts import connect_to_hosts, disconnect_from_hosts

# Define the script directory (root level now)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    """Parse command-line arguments and execute specified actions."""
    parser = argparse.ArgumentParser(description="Network device automation tool")
    parser.add_argument('--actions', nargs='+',
                        choices=['interfaces', 'bgp', 'ospf', 'ldp', 'rsvp', 'mpls',
                                 'ping', 'bgp_verification', 'ospf_verification',
                                 'backup', 'baseline', 'route_monitor'],
                        help="Actions to perform (e.g., 'ping', 'backup')")
    args = parser.parse_args()

    # Paths relative to root directory
    inventory_file = os.path.join(SCRIPT_DIR, "data/inventory.yml")
    hosts_data_file = os.path.join(SCRIPT_DIR, "data/hosts_data.yml")

    merged_data = merge_host_data(inventory_file, hosts_data_file)
    if not merged_data:
        print("Failed to load or merge data. Exiting.")
        return

    username = merged_data['username']
    password = merged_data['password']
    hosts = merged_data['hosts']
    host_ips = [host['ip_address'] for host in hosts]
    interval = merged_data['interval']

    if not args.actions:
        print("No actions specified. Use --actions with one or more of:", parser.parse_args(['--help']).actions)
        return

    if 'ping' in args.actions:
        from scripts.verification_actions import ping_hosts
        ping_hosts(
            username=username,
            password=password,
            host_ips=host_ips,
            hosts=hosts,
            connect_to_hosts=connect_to_hosts,
            disconnect_from_hosts=disconnect_from_hosts
        )

    print(f"Completed actions: {args.actions}")

if __name__ == "__main__":
    main()
