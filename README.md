---

### README.md

```markdown
# Vectautomation

A Python-based tool for automating network device management tasks on Junos devices, including pinging hosts, configuring interfaces, and verifying BGP sessions.

## Directory Structure

```
/home/nikos/github/ngeran/vectautomation/
├── data/
│   ├── hosts_data.yml      # Device configurations (interfaces, BGP, etc.)
│   └── inventory.yml       # Inventory of devices by location and type
├── main.py                 # Entry point for running actions
├── README.md               # Project documentation
├── scripts/
│   ├── actions.py          # Maps action names to functions
│   ├── connect_to_hosts.py # SSH connection handling for Junos devices
│   ├── interface_actions.py # Interface configuration (Layer 2/3, MPLS)
│   ├── utils.py            # YAML loading and data merging utilities
│   ├── verification_actions.py # Verification tasks (ping, BGP)
│   └── __pycache__/        # Python cache files
├── templates/
│   └── interface_template.j2 # Jinja2 template for interface configs
├── reports/
│   ├── ping_report_*.txt   # Ping verification reports
│   └── bgp_report_*.txt    # BGP verification reports
```

## Running the Scripts

### Prerequisites

1. **Python Environment**:
   - Python 3.8+ is required.
   - Install dependencies:
     ```bash
     pip install junos-eznc ncclient pyyaml jinja2 lxml
     ```
   - If using a Nix environment, ensure these packages are included.

2. **Configuration Files**:
   - Ensure `data/hosts_data.yml` contains device details (e.g., IPs, interfaces, BGP configs).
   - Ensure `data/inventory.yml` lists devices by location (optional for merging metadata).
   - Example `hosts_data.yml`:
     ```yaml
     username: admin
     password: manolis1
     hosts:
       - host_name: DC1MX480PE-1
         ip_address: 172.27.200.200
         interfaces:
           - name: ge-0/0/3
             ip_address: 172.27.201.1/24
       - host_name: SP1DCI106BJEX01
         ip_address: 172.27.200.201
     ```

3. **Network Access**:
   - Devices must be reachable via SSH (port 22).
   - Verify with:
     ```bash
     ssh admin@172.27.200.200
     ```

### Basic Command

Run from the project root:
```bash
cd /home/nikos/github/ngeran/vectautomation
python main.py --actions <action1> [action2 ...]
```

### Available Actions

- `ping`: Verifies reachability between devices, saving a report to `reports/ping_report_<timestamp>.txt`.
- `interfaces`: Configures Layer 2/3 and MPLS interfaces using `templates/interface_template.j2`.
- `bgp_verification`: Checks BGP neighbor states, saving a report to `reports/bgp_report_<timestamp>.txt`.
- Others (not yet implemented): `bgp`, `ospf`, `ldp`, `rsvp`, `mpls`, `ospf_verification`, `backup`, `baseline`, `route_monitor`.

### Examples

1. **Ping Verification**:
   ```bash
   python main.py --actions ping
   ```
   **Output**:
   ```
   Warning: Host 'DC1MX480PE-2' in inventory.yml not found in hosts_data.yml
   ...
   Executing action: ping
   INFO:ncclient.transport.ssh:Connected (version 2.0, client OpenSSH_6.9)
   INFO:ncclient.transport.ssh:Authentication (password) successful!
   Connected to 172.27.200.200
   INFO:ncclient.transport.ssh:Connected (version 2.0, client OpenSSH_6.9)
   INFO:ncclient.transport.ssh:Authentication (password) successful!
   Connected to 172.27.200.201
   Ping report saved to /home/nikos/github/ngeran/vectautomation/reports/ping_report_20250409_123456.txt
   Disconnected from 172.27.200.200 (172.27.200.200)
   Disconnected from 172.27.200.201 (172.27.200.201)
   Completed actions: ['ping']
   ```

2. **Configure Interfaces**:
   ```bash
   python main.py --actions interfaces
   ```
   **Output**:
   ```
   Warning: Host 'DC1MX480PE-2' in inventory.yml not found in hosts_data.yml
   ...
   Executing action: interfaces
   Connected to 172.27.200.200
   Connected to 172.27.200.201
   Interfaces configured for DC1MX480PE-1 (172.27.200.200)
   Interfaces configured for SP1DCI106BJEX01 (172.27.200.201)
   Disconnected from 172.27.200.200 (172.27.200.200)
   Disconnected from 172.27.200.201 (172.27.200.201)
   Completed actions: ['interfaces']
   ```

3. **Multiple Actions**:
   ```bash
   python main.py --actions ping bgp_verification
   ```
   **Output**:
   ```
   Warning: Host 'DC1MX480PE-2' in inventory.yml not found in hosts_data.yml
   ...
   Executing action: ping
   Connected to 172.27.200.200
   Connected to 172.27.200.201
   Ping report saved to /home/nikos/github/ngeran/vectautomation/reports/ping_report_20250409_123456.txt
   Disconnected from 172.27.200.200 (172.27.200.200)
   Disconnected from 172.27.200.201 (172.27.200.201)
   Executing action: bgp_verification
   Connected to 172.27.200.200
   Connected to 172.27.200.201
   BGP report saved to /home/nikos/github/ngeran/vectautomation/reports/bgp_report_20250409_123456.txt
   Disconnected from 172.27.200.200 (172.27.200.200)
   Disconnected from 172.27.200.201 (172.27.200.201)
   Completed actions: ['ping', 'bgp_verification']
   ```

### Notes

- **Configuration**: Update `hosts_data.yml` with correct IPs and credentials.
- **Reports**: Check `reports/` for outputs (e.g., `ping_report_*.txt`).
- **Interruptions**: Press `Ctrl+C` to stop cleanly:
  ```
  Ping action interrupted by user.
  Disconnected from 172.27.200.200 (172.27.200.200)
  Script interrupted by user.
  ```
- **Logging**: Shows `Connected` and `Authentication` logs; `Sending` is suppressed.
- **Troubleshooting**:
  - Verify SSH access if devices are unreachable.
  - Check `hosts_data.yml` for errors.
  - Update dependencies:
    ```bash
    pip install --upgrade junos-eznc ncclient pyyaml jinja2 lxml
    ```
```

---

### Instructions
1. **Copy and Paste**:
   - Copy the entire Markdown block above.
   - Open `/home/nikos/github/ngeran/vectautomation/README.md` in a text editor.
   - Paste the content, overwriting the existing `README.md` or appending as needed.
   - Save the file.

2. **Verify**:
   - Check the file renders correctly in a Markdown viewer (e.g., GitHub, VS Code).
   - Run a command to confirm it works:
     ```bash
     python main.py --actions ping
     ```

---

### Notes
- **Content**: Includes directory structure, prerequisites, how to run `main.py`, available actions, and example outputs, tailored to your project.
- **Examples**: Covers `ping`, `interfaces`, and `ping bgp_verification`, matching your current functionality.
- **Clarity**: Kept it concise with troubleshooting tips for common issues (e.g., SSH, dependencies).
- **Future**: We can add new actions (e.g., `ospf_verification`) to the README as we implement them.

---

### Next Steps
- Save this to `README.md` and let me know if you want tweaks (e.g., add a project overview, license, or logos).
- With `ping` working and logs adjusted, we could:
  - Add `ospf_verification` to check OSPF neighbors.
  - Implement BGP/OSPF configs in `interface_actions.py`.
  - Start `backup` or `route_monitor`.
- Any other changes? (e.g., file logging, more actions)

Does this look good? Let me know if you need help saving it or what’s next!
