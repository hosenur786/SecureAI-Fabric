import time
import uuid
import json
from datetime import datetime, timezone
from pathlib import Path
from network.topology import build_topology
from scenarios.network_traffic import (
    normal_traffic,
    moderate_rate_traffic,
    high_rate_traffic
)
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


def get_node_label(scenario_name, node_name):
    """
    Determine whether a specific GPU node is normal or anomalous
    for the current controlled scenario.
    """

    anomalous_nodes = {
        "NORMAL TRAFFIC": set(),
        "MODERATE-RATE TRAFFIC": set(),
        "HIGH-RATE TRAFFIC": {"GPU-01", "GPU-02"},
    }

    if scenario_name not in anomalous_nodes:
        raise ValueError(
            f"Unknown scenario: {scenario_name}"
        )

    if node_name in anomalous_nodes[scenario_name]:
        return "anomalous"

    return "normal"


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
    experiment_id = str(uuid.uuid4())

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

    for item in after_stats:
        item["experiment_id"] = experiment_id
        item["scenario"] = scenario_name
        item["node_label"] = get_node_label(
            scenario_name,
            item["node"]
        )
        item["scenario_duration_s"] = round(elapsed_time, 3)

    # Save the experiment results.
    save_records(after_stats)

    print(f"Elapsed time: {elapsed_time:.3f} seconds")

    for item in after_stats:
        print(item)


def run_repeated_experiments(net, repetitions=3):
    """
    Run multiple repetitions of each network scenario.
    """

    for i in range(repetitions):
        print(f"\n========== Repetition {i + 1} ==========")

        run_experiment(
            net,
            normal_traffic,
            "NORMAL TRAFFIC"
        )

        run_experiment(
            net,
            moderate_rate_traffic,
            "MODERATE-RATE TRAFFIC"
        )

        run_experiment(
            net,
            high_rate_traffic,
            "HIGH-RATE TRAFFIC"
        )


def main():
    net = build_topology(gpu_count=6)

    try:
        net.start()

        run_repeated_experiments(
            net,
            repetitions=3
        )

    finally:
        net.stop()


if __name__ == "__main__":
    main()
