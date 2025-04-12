# /home/nikos/github/ngeran/vectautomation/scripts/interface_actions.py
import os
from jinja2 import Environment, FileSystemLoader
from jnpr.junos.utils.config import Config

def render_interface_template(host):
    """
    Render the Jinja2 interface template for a host’s interfaces.

    Args:
        host (dict): Host data from hosts_data.yml (includes interfaces).

    Returns:
        str: Rendered configuration string, or None if failed.
    """
    try:
        # Set up Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '../templates')
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('interface_template.j2')

        # Render template for each interface
        config = ""
        for interface in host.get('interfaces', []):
            config += template.render(interface=interface)
        return config
    except Exception as error:
        print(f"Failed to render template for {host['host_name']}: {error}")
        return None

def configure_interfaces(username, password, host_ips, hosts, connect_to_hosts, disconnect_from_hosts):
    """
    Configure interfaces on devices using rendered Jinja2 templates.

    Args:
        username (str): SSH username.
        password (str): SSH password.
        host_ips (list): List of host IPs to configure.
        hosts (list): List of host dicts from hosts_data.yml.
        connect_to_hosts (function): Function to establish SSH connections.
        disconnect_from_hosts (function): Function to close SSH connections.
    """
    connections = connect_to_hosts(username, password, host_ips)
    if not connections:
        print("No devices connected for interface configuration.")
        return

    host_lookup = {h['ip_address']: h for h in hosts}
    for dev in connections:
        host = host_lookup.get(dev.hostname)
        if not host:
            print(f"No host data for {dev.hostname}, skipping.")
            continue

        config_str = render_interface_template(host)
        if not config_str:
            print(f"Skipping configuration for {host['host_name']} due to rendering failure.")
            continue

        try:
            with Config(dev, mode='exclusive') as cu:
                cu.load(config_str, format='text')
                cu.commit()
                print(f"Interfaces configured for {host['host_name']} ({dev.hostname})")
        except Exception as error:
            print(f"Failed to configure interfaces for {host['host_name']} ({dev.hostname}): {error}")

    disconnect_from_hosts(connections)
