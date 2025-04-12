# /home/nikos/github/ngeran/vectautomation/scripts/interface_actions.py
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConfigLoadError, CommitError
from jinja2 import Environment, FileSystemLoader
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_interfaces(username, password, host_ips, hosts, connect_to_hosts, disconnect_from_hosts):
    """Configure interfaces on devices based on hosts_data.yml."""
    template_dir = os.path.join(os.path.dirname(__file__), '../templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('interface_template.j2')

    connections = []
    try:
        connections = connect_to_hosts(username, password, host_ips)
        if not connections:
            print("No devices connected for interface configuration.")
            return

        host_lookup = {h['ip_address']: h for h in hosts}
        for dev in connections:
            host_ip = dev.hostname
            host = host_lookup.get(host_ip)
            if not host or 'interfaces' not in host:
                print(f"No interfaces defined for {host.get('host_name', host_ip)} ({host_ip}), skipping.")
                continue

            try:
                config_data = {
                    'interfaces': host['interfaces'],
                    'host_name': host['host_name']
                }
                config_text = template.render(**config_data)

                with Config(dev, mode='exclusive') as cu:
                    cu.load(config_text, format='text')
                    cu.commit()
                print(f"Interfaces configured for {host['host_name']} ({host_ip})")
            except (ConfigLoadError, CommitError) as error:
                print(f"Failed to configure interfaces for {host['host_name']} ({host_ip}): {error}")
            except Exception as error:
                print(f"Unexpected error for {host['host_name']} ({host_ip}): {error}")

    except KeyboardInterrupt:
        print("Interface configuration interrupted by user.")
        raise
    finally:
        if connections:
            disconnect_from_hosts(connections)
