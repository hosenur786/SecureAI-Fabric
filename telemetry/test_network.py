from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

from telemetry.network import collect_cluster_stats


def main():
    net = Mininet(
        switch=OVSSwitch,
        controller=None,
        link=TCLink
    )

    switch = net.addSwitch(
        "s1",
        dpid="0000000000000001",
        failMode="standalone"
    )

    for i in range(1, 7):
        gpu_name = f"GPU-{i:02d}"
        ip_address = f"10.0.0.{i}/24"

        host = net.addHost(
            gpu_name,
            ip=ip_address
        )

        net.addLink(host, switch)

    try:
        net.start()

        stats = collect_cluster_stats(net)

        for item in stats:
            print(item)

    finally:
        net.stop()


if __name__ == "__main__":
    main()
