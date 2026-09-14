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
    }
