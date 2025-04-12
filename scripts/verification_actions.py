# /home/nikos/github/ngeran/vectautomation/scripts/verification_actions.py
import os
from datetime import datetime
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def ping_hosts(username, password, host_ips, hosts, connect_to_hosts, disconnect_from_hosts):
    """Verify reachability by pinging hosts from each device and generate a report."""
    report_dir = os.path.join(os.path.dirname(__file__), '../reports')
    os.makedirs(report_dir, exist_ok=True)

    connections = []
    try:
        connections = connect_to_hosts(username, password, host_ips)
        if not connections:
            print("No devices connected for ping verification.")
            return

        # Only ping between successfully connected devices
        connected_ips = [dev.hostname for dev in connections]
        host_lookup = {h['ip_address']: h['host_name'] for h in hosts}
        reachable = []
        unreachable = []

        for dev in connections:
            source_host = host_lookup.get(dev.hostname, dev.hostname)
            for target_ip in connected_ips:
                if target_ip == dev.hostname:
                    continue
                target_host = host_lookup.get(target_ip, target_ip)
                try:
                    # Enforce 5-second timeout for ping
                    with timeout(5):
                        ping_result = dev.rpc.cli(f"ping {target_ip} count 4", format='text')
                    ping_output = ping_result.text
                    if " 0% packet loss" in ping_output:
                        reachable.append(f"{source_host} ({dev.hostname}) can reach {target_host} ({target_ip})")
                    else:
                        unreachable.append(f"{source_host} ({dev.hostname}) cannot reach {target_host} ({target_ip})")
                except TimeoutError:
                    unreachable.append(f"{source_host} ({dev.hostname}) ping to {target_host} ({target_ip}) timed out")
                except Exception as error:
                    unreachable.append(f"{source_host} ({dev.hostname}) ping to {target_ip} failed: {error}")

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

    except KeyboardInterrupt:
        print("Ping action interrupted by user.")
        raise  # Re-raise to allow higher-level handling
    finally:
        if connections:
            disconnect_from_hosts(connections)

def bgp_verification(username, password, host_ips, hosts, connect_to_hosts, disconnect_from_hosts):
    """Verify BGP neighbor states and generate a report."""
    report_dir = os.path.join(os.path.dirname(__file__), '../reports')
    os.makedirs(report_dir, exist_ok=True)

    connections = []
    try:
        connections = connect_to_hosts(username, password, host_ips)
        if not connections:
            print("No devices connected for BGP verification.")
            return

        host_lookup = {h['ip_address']: h for h in hosts}
        up_peers = []
        down_peers = []

        for dev in connections:
            host_ip = dev.hostname
            host = host_lookup.get(host_ip)
            if not host or 'bgp' not in host:
                print(f"No BGP configuration for {host.get('host_name', host_ip)} ({host_ip}), skipping.")
                continue

            source_host = host['host_name']
            bgp_config = host['bgp']
            expected_peers = {peer['peer_ip']: peer for peer in bgp_config.get('peers', [])}

            try:
                with timeout(5):
                    bgp_info = dev.rpc.get_bgp_neighbor_information()
                for neighbor in bgp_info.findall('.//bgp-neighbor'):
                    peer_ip = neighbor.findtext('peer-address')
                    peer_state = neighbor.findtext('peer-state')
                    if peer_ip in expected_peers:
                        peer_as = expected_peers[peer_ip]['peer_as']
                        if peer_state.lower() == 'established':
                            up_peers.append(f"{source_host} ({host_ip}) BGP peer {peer_ip} (AS {peer_as}) is UP")
                        else:
                            down_peers.append(f"{source_host} ({host_ip}) BGP peer {peer_ip} (AS {peer_as}) is DOWN ({peer_state})")
                    else:
                        print(f"Unexpected BGP peer {peer_ip} on {source_host} ({host_ip})")
            except TimeoutError:
                down_peers.append(f"{source_host} ({host_ip}) BGP verification timed out")
            except Exception as error:
                down_peers.append(f"{source_host} ({host_ip}) BGP verification failed: {error}")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report = f"BGP Verification Report - {timestamp}\n{'='*50}\n"
        report += "\nUp Peers:\n"
        for entry in up_peers:
            report += f"  - {entry}\n"
        report += "\nDown Peers:\n"
        for entry in down_peers:
            report += f"  - {entry}\n"

        report_file = os.path.join(report_dir, f"bgp_report_{timestamp}.txt")
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"BGP report saved to {report_file}")

    except KeyboardInterrupt:
        print("BGP verification interrupted by user.")
        raise
    finally:
        if connections:
            disconnect_from_hosts(connections)
