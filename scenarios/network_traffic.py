def normal_traffic(net):
    """
    Generate low-volume normal traffic between selected GPU nodes.

    Returns:
        A list containing the ping command results.
    """

    gpu1 = net.get("GPU-01")
    gpu3 = net.get("GPU-03")
    gpu5 = net.get("GPU-05")

    results = []

    results.append(
        gpu1.cmd("ping -c 5 10.0.0.2")
    )

    results.append(
        gpu3.cmd("ping -c 5 10.0.0.4")
    )

    results.append(
        gpu5.cmd("ping -c 5 10.0.0.6")
    )

    return results


def high_rate_traffic(
    net,
    source="GPU-01",
    destination="10.0.0.2",
    count=100,
    interval=0.01
):
    """
    Generate controlled high-rate ICMP traffic.

    Args:
        net: Active Mininet network.
        source: Source GPU node name.
        destination: Destination IP address.
        count: Number of ICMP packets.
        interval: Delay between packets in seconds.

    Returns:
        The ping command result.
    """

    source_gpu = net.get(source)

    return source_gpu.cmd(
        f"ping -c {count} -i {interval} {destination}"
    )


def moderate_rate_traffic(
    net,
    source="GPU-01",
    destination="10.0.0.2",
    count=50,
    interval=0.05
):
    """
    Generate controlled moderate-rate ICMP traffic.

    Args:
        net: Active Mininet network.
        source: Source GPU node name.
        destination: Destination IP address.
        count: Number of ICMP packets.
        interval: Delay between packets in seconds.

    Returns:
        The ping command result.
    """

    source_gpu = net.get(source)

    return source_gpu.cmd(
        f"ping -c {count} -i {interval} {destination}"
    )
