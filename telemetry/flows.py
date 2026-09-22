import re
import subprocess


def get_ovs_flows(switch_name="s1"):
    """
    Collect OpenFlow entries from an Open vSwitch switch.

    Returns:
        Raw flow output from ovs-ofctl.
    """

    result = subprocess.run(
        [
            "ovs-ofctl",
            "dump-flows",
            switch_name,
            "-O",
            "OpenFlow13"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout


def parse_flow_line(line):
    """
    Parse one Open vSwitch IP flow entry.

    Returns:
        A dictionary containing useful flow fields,
        or None if the entry is not a usable IP flow.
    """

    if "n_packets=" not in line:
        return None

    # Only keep flows that contain IP source and destination fields.
    src_match = re.search(r"nw_src=([0-9.]+)", line)
    dst_match = re.search(r"nw_dst=([0-9.]+)", line)

    if not src_match or not dst_match:
        return None

    flow = {
        "src_ip": src_match.group(1),
        "dst_ip": dst_match.group(1),
    }

    match = re.search(r"n_packets=(\d+)", line)
    if match:
        flow["packets"] = int(match.group(1))

    match = re.search(r"n_bytes=(\d+)", line)
    if match:
        flow["bytes"] = int(match.group(1))

    match = re.search(r"priority=(\d+)", line)
    if match:
        flow["priority"] = int(match.group(1))

    if "icmp" in line:
        flow["protocol"] = "ICMP"
    elif "tcp" in line:
        flow["protocol"] = "TCP"
    elif "udp" in line:
        flow["protocol"] = "UDP"
    else:
        flow["protocol"] = "IP"

    return flow


def collect_flow_stats(switch_name="s1"):
    """
    Collect and parse usable IP flow entries.

    Returns:
        A list of parsed flow dictionaries.
    """

    raw_output = get_ovs_flows(switch_name)

    flows = []

    for line in raw_output.splitlines():
        flow = parse_flow_line(line)

        if flow is not None:
            flows.append(flow)

    return flows
