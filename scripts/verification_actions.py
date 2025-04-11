# /home/nikos/github/ngeran/vectautomation/scripts/verification_actions.py
import os
from datetime import datetime

def ping_hosts(username, password, host_ips, hosts, connect_to_hosts, disconnect_from_hosts):
    """Ping hosts from each device via SSH and generate a reachability report."""
    # Create reports folder in root directory
    report_dir = os.path.join(os.path.dirname(__file__), '../reports')
    os.makedirs(report_dir, exist_ok=True)

    connections = connect_to_hosts(username, password, host_ips)
    if not connections:
        print("No devices connected for ping verification.")
        return

    host_lookup = {h['ip_address']: h['host_name'] for h in hosts}
    reachable = []
    unreachable = []

    for dev in connections:
        source_host = host_lookup.get(dev.hostname, dev.hostname)
        for target_ip in host_ips:
            if target_ip == dev.hostname:  # Skip self-ping
                continue
            target_host = host_lookup.get(target_ip, target_ip)
            try:
                ping_result = dev.rpc.cli(f"ping {target_ip} count 4", format='text')
                ping_output = ping_result.text
                if " 0% packet loss" in ping_output:
                    reachable.append(f"{source_host} ({dev.hostname}) can reach {target_host} ({target_ip})")
                else:
                    unreachable.append(f"{source_host} ({dev.hostname}) cannot reach {target_host} ({target_ip})")
            except Exception as error:
                unreachable.append(f"{source_host} ({dev.hostname}) ping to {target_host} ({target_ip}) failed: {error}")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report = f"Ping Verification Report - {timestamp}\n{'='*50}\n"
    report += "\nReachable:\n"
    for entry in reachable:
        report += f"  - {entry}\n"
    report += "\nUnreachable:\n"
    for entry in unreachable:
        report += f"  - {entry}\n"

    report_file = os.path.join(report_dir, f"ping_report_{timestamp}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"Ping report saved to {report_file}")

    disconnect_from_hosts(connections)
