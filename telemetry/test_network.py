from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

from telemetry.network import read_interface_stats


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

    gpu1 = net.addHost(
        "GPU-01",
        ip="10.0.0.1/24"
    )

    net.addLink(gpu1, switch)

    try:
        net.start()

        stats = read_interface_stats(gpu1)

        print(stats)

    finally:
        net.stop()


if __name__ == "__main__":
    main()
