from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


def build_topology(gpu_count=6):
    """
    Create a simulated GPU cluster.

    Parameters:
        gpu_count: Number of virtual GPU nodes to create.
    """

    net = Mininet(
        switch=OVSSwitch,
        controller=None,
        link=TCLink
    )

    info(f"*** Creating SecureAI-Fabric with {gpu_count} GPU nodes\n")

    # Create the OVS switch
    switch = net.addSwitch(
       "s1",
       dpid="0000000000000001",
       failMode="standalone"
     )

    # Create virtual GPU nodes
    for i in range(1, gpu_count + 1):
        gpu_name = f"GPU-{i:02d}"
        ip_address = f"10.0.0.{i}/24"

        host = net.addHost(
            gpu_name,
            ip=ip_address
        )

        net.addLink(host, switch)

        info(
            f"*** Added {gpu_name} "
            f"with IP {ip_address}\n"
        )

    return net


def main():
    setLogLevel("info")

    net = build_topology(gpu_count=6)

    try:
        info("*** Starting SecureAI-Fabric network\n")
        net.start()

        info("*** Network started successfully\n")
        info("*** Running CLI. Type 'exit' to shut down the network.\n")

        CLI(net)

    finally:
        info("*** Stopping SecureAI-Fabric network\n")
        net.stop()


if __name__ == "__main__":
    main()
