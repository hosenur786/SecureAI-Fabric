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

def install_icmp_monitoring_rules(switch_name="s1"):
    """
    Install ICMP flow-monitoring rules for the traffic
    patterns used by SecureAI-Fabric experiments.
    """

    monitored_flows = [
        ("10.0.0.1", "10.0.0.2"),
        ("10.0.0.3", "10.0.0.4"),
        ("10.0.0.5", "10.0.0.6"),
    ]

    for src_ip, dst_ip in monitored_flows:
        subprocess.run(
            [
                "ovs-ofctl",
                "-O",
                "OpenFlow13",
                "add-flow",
                switch_name,
                (
                    "priority=110,"
                    f"icmp,nw_src={src_ip},"
                    f"nw_dst={dst_ip},"
                    "actions=NORMAL"
                )
            ],
            check=True
        )


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

def calculate_flow_rates(previous_flows, current_flows, elapsed_time):
    """
    Calculate packet and byte rates for observed flows.

    Returns:
        Current flow records with delta and per-second fields.
    """

    if elapsed_time <= 0:
        elapsed_time = 1.0

    previous_lookup = {
        (
            flow["src_ip"],
            flow["dst_ip"],
            flow["protocol"]
        ): flow
        for flow in previous_flows
    }

    results = []

    for current in current_flows:
        key = (
            current["src_ip"],
            current["dst_ip"],
            current["protocol"]
        )

        previous = previous_lookup.get(key)

        if previous is None:
            previous_packets = 0
            previous_bytes = 0
        else:
            previous_packets = previous["packets"]
            previous_bytes = previous["bytes"]

        packet_delta = current["packets"] - previous_packets
        byte_delta = current["bytes"] - previous_bytes

        flow = current.copy()

        flow["packet_delta"] = packet_delta
        flow["byte_delta"] = byte_delta
        flow["packets_per_sec"] = packet_delta / elapsed_time
        flow["bytes_per_sec"] = byte_delta / elapsed_time

        results.append(flow)

    return results


def save_flow_records(
    flow_records,
    experiment_id,
    scenario,
    scenario_parameters=None,
    file_path="data/flow_experiments.jsonl"
):
    """
    Save flow telemetry records to a JSON Lines file.

    Each flow record is enriched with experiment metadata.
    """

    from pathlib import Path
    import json

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    scenario_parameters = scenario_parameters or {}

    with path.open("a", encoding="utf-8") as file:
        for flow in flow_records:
            record = flow.copy()

            record["experiment_id"] = experiment_id
            record["scenario"] = scenario
            record["scenario_parameters"] = scenario_parameters

            file.write(
                json.dumps(record) + "\n"
            )
