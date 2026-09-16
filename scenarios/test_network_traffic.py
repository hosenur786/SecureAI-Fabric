from network.topology import build_topology
from scenarios.network_traffic import normal_traffic, high_rate_traffic


def main():
    net = build_topology(gpu_count=6)

    try:
        net.start()

        print("\n--- Normal traffic ---")
        for result in normal_traffic(net):
            print(result)

        print("\n--- High-rate traffic ---")
        print(high_rate_traffic(net))

    finally:
        net.stop()


if __name__ == "__main__":
    main()
