from network.topology import build_topology
from telemetry.flows import collect_flow_stats
import subprocess

def find_flow(flows, src_ip, dst_ip, protocol):
    """
    Find a flow matching source, destination, and protocol.
    """

    for flow in flows:
        if (
            flow.get("src_ip") == src_ip
            and flow.get("dst_ip") == dst_ip
            and flow.get("protocol") == protocol
        ):
            return flow

    return None


def main():
    net = build_topology(6)

    try:
        net.start()

        subprocess.run(
            [
                "ovs-ofctl",
                "-O",
                "OpenFlow13",
                "add-flow",
                "s1",
                "priority=110,icmp,nw_src=10.0.0.1,"
                "nw_dst=10.0.0.2,actions=NORMAL"
            ],
            check=True
        )

        print("\n--- Flows before traffic ---")
        before_flows = collect_flow_stats("s1")

        before = find_flow(
            before_flows,
            "10.0.0.1",
            "10.0.0.2",
            "ICMP"
        )

        print("ICMP flow before:", before)

        print("\n--- Generating traffic ---")
        gpu1 = net.get("GPU-01")

        result = gpu1.cmd(
            "ping -c 5 10.0.0.2"
        )

        print(result)

        print("\n--- Flows after traffic ---")
        after_flows = collect_flow_stats("s1")

        after = find_flow(
            after_flows,
            "10.0.0.1",
            "10.0.0.2",
            "ICMP"
        )

        print("ICMP flow after:", after)

        if before and after:
            print(
                "\nPacket increase:",
                after["packets"] - before["packets"]
            )

            print(
                "Byte increase:",
                after["bytes"] - before["bytes"]
            )

    finally:
        net.stop()


if __name__ == "__main__":
    main()
