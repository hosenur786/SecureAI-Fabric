import time

from datetime import datetime, timezone
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

from telemetry.network import collect_cluster_stats, add_rates


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

        # Take the first telemetry sample.
        start_time = time.time()
        previous_stats = collect_cluster_stats(net)

        # Wait before taking the second sample.
        time.sleep(2)

        # Take the second telemetry sample.
        current_stats = collect_cluster_stats(net)
        end_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        elapsed_time = end_time - start_time

        for current in current_stats:
            current["timestamp"] = timestamp

        # Add traffic rates to each current sample.
        for previous, current in zip(previous_stats, current_stats):
            add_rates(
                previous,
                current,
                elapsed_time
            )

        for item in current_stats:
            print(item)

    finally:
        net.stop()


if __name__ == "__main__":
    main()
