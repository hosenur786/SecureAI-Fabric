import time
import json
from datetime import datetime, timezone
from pathlib import Path
from network.topology import build_topology
from scenarios.network_traffic import normal_traffic, high_rate_traffic
from telemetry.network import collect_cluster_stats, add_rates


def collect_sample(net):
    """
    Collect one timestamped cluster telemetry sample.
    """

    timestamp = datetime.now(timezone.utc).isoformat()

    stats = collect_cluster_stats(net)

    for item in stats:
        item["timestamp"] = timestamp

    return stats

def save_records(records, file_path="data/network_experiments.jsonl"):
    """
    Append telemetry records to a JSON Lines file.
    """

    path = Path(file_path)

    # Create the data directory if it does not exist.
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record) + "\n")


def run_experiment(net, scenario_function, scenario_name):
    """
    Run one traffic scenario and measure its network behavior.
    """

    print(f"\n=== {scenario_name} ===")

    # Measure the network before the scenario.
    before_stats = collect_sample(net)
    # Measure only the time spent executing the scenario.
    scenario_start = time.monotonic()

    # Generate the traffic scenario.
    scenario_function(net)
    scenario_end = time.monotonic()

    # Measure the network after the scenario.
    after_stats = collect_sample(net)

    elapsed_time = scenario_end - scenario_start

    # Calculate traffic rates.
    for before, after in zip(before_stats, after_stats):
        add_rates(
            before,
            after,
            elapsed_time
        )

    # Add experiment metadata to each telemetry record.
    for item in after_stats:
        item["scenario"] = scenario_name
        item["scenario_duration_s"] = round(elapsed_time, 3)

    # Save the experiment results.
    save_records(after_stats)

    print(f"Elapsed time: {elapsed_time:.3f} seconds")

    for item in after_stats:
        print(item)




def main():
    net = build_topology(gpu_count=6)

    try:
        net.start()

        # Run the normal traffic experiment.
        run_experiment(
            net,
            normal_traffic,
            "NORMAL TRAFFIC"
        )

        # Run the high-rate traffic experiment.
        run_experiment(
            net,
            high_rate_traffic,
            "HIGH-RATE TRAFFIC"
        )

    finally:
        net.stop()


if __name__ == "__main__":
    main()
