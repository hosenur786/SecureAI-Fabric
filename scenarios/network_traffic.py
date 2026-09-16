def normal_traffic(net):
    """
    Generate low-volume normal traffic between selected GPU nodes.

    Returuns:
          A list containing the ping command results.
    """

    gpu1 = net.get("GPU-01")
    gpu3 = net.get("GPU-03")
    gpu5 = net.get("GPU-05")

    results = []


    results.append(gpu1.cmd("ping -c 5 10.0.0.2"))
    results.append(gpu3.cmd("ping -c 5 10.0.0.4"))
    results.append(gpu5.cmd("ping -c 5 10.0.0.6"))

    return results


def high_rate_traffic(net):
    """
    Generate controlled high-rate ICMP traffic between two GPU nodes.
    """

    gpu1 = net.get("GPU-01")

    return gpu1.cmd("ping -c 100 -i 0.01 10.0.0.2")
