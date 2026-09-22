def read_interface_stats(host):
    """
    Read network statistics from a Mininet host.

    The host's default network interface is detected automatically.

    Returns:
        A dictionary containing RX/TX bytes and packets.
    """

    interface = host.defaultIntf().name

    rx_bytes = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/rx_bytes"
    ).strip()

    rx_packets = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/rx_packets"
    ).strip()
    rx_dropped = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/rx_dropped"
    ).strip()

    tx_dropped = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/tx_dropped"
    ).strip()

    tx_bytes = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/tx_bytes"
    ).strip()

    tx_packets = host.cmd(
        f"cat /sys/class/net/{interface}/statistics/tx_packets"
    ).strip()

    return {
        "node": host.name,
        "interface": interface,
        "rx_bytes": int(rx_bytes),
        "rx_packets": int(rx_packets),
        "tx_bytes": int(tx_bytes),
        "tx_packets": int(tx_packets),
        "rx_dropped": int(rx_dropped),
        "tx_dropped": int(tx_dropped),
    }


def collect_cluster_stats(net):
    """
    Collect network statistics from all GPU nodes in the Mininet network.

    Returns:
        A list containing telemetry dictionaries for each GPU node.
    """

    stats = []

    for host in net.hosts:
        host_stats = read_interface_stats(host)
        stats.append(host_stats)

    return stats


def calculate_rate(old_value, new_value, elapsed_time):
    """
    Calculate the rate of change between two counter values.

    Args:
        old_value: Counter value from the previous sample.
        new_value: Counter value from the current sample.
        elapsed_time: Time between samples in seconds.

    Returns:
        Rate per second.
    """

    if elapsed_time <= 0:
        return 0.0

    return (new_value - old_value) / elapsed_time


def add_rates(previous, current, elapsed_time):
    """
    Add traffic rates to a current telemetry sample.

    Args:
        previous: Previous telemetry dictionary.
        current: Current telemetry dictionary.
        elapsed_time: Time between samples in seconds.

    Returns:
        Current telemetry dictionary with rate fields added.
    """

    current["rx_bytes_per_sec"] = calculate_rate(
        previous["rx_bytes"],
        current["rx_bytes"],
        elapsed_time
    )

    current["rx_packets_per_sec"] = calculate_rate(
        previous["rx_packets"],
        current["rx_packets"],
        elapsed_time
    )
    
    current["rx_dropped_per_sec"] = calculate_rate(
        previous["rx_dropped"],
        current["rx_dropped"],
        elapsed_time
    )

    current["tx_dropped_per_sec"] = calculate_rate(
        previous["tx_dropped"],
        current["tx_dropped"],
        elapsed_time
    )

    current["tx_bytes_per_sec"] = calculate_rate(
        previous["tx_bytes"],
        current["tx_bytes"],
        elapsed_time
    )

    current["tx_packets_per_sec"] = calculate_rate(
        previous["tx_packets"],
        current["tx_packets"],
        elapsed_time
    )

    return current
