import json


FLOW_PATH = "data/flow_experiments.jsonl"
NETWORK_PATH = "data/network_experiments.jsonl"


FLOW_PAIR_TO_NODES = {
    ("10.0.0.1", "10.0.0.2"): ("GPU-01", "GPU-02"),
    ("10.0.0.3", "10.0.0.4"): ("GPU-03", "GPU-04"),
    ("10.0.0.5", "10.0.0.6"): ("GPU-05", "GPU-06"),
}


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def build_flow_node_records(
    flow_path=FLOW_PATH,
    network_path=NETWORK_PATH
):
    """
    Convert flow-level records into node-level records.

    Each monitored flow is associated with its source and
    destination GPU node.
    """

    flow_records = load_jsonl(flow_path)
    network_records = load_jsonl(network_path)

    # Get the label and scenario information for each node/experiment.
    metadata = {}

    for record in network_records:
        key = (
            record["experiment_id"],
            record["node"]
        )

        metadata[key] = {
            "scenario": record["scenario"],
            "scenario_parameters": record["scenario_parameters"],
            "node_label": record["node_label"],
        }

    node_records = []

    for flow in flow_records:
        pair = (
            flow["src_ip"],
            flow["dst_ip"]
        )

        nodes = FLOW_PAIR_TO_NODES.get(pair)

        if nodes is None:
            continue

        for node in nodes:
            key = (
                flow["experiment_id"],
                node
            )

            if key not in metadata:
                continue

            record = {
                "experiment_id": flow["experiment_id"],
                "node": node,
                "scenario": metadata[key]["scenario"],
                "scenario_parameters": metadata[key]["scenario_parameters"],
                "node_label": metadata[key]["node_label"],
                "flow_packets_per_sec": flow["packets_per_sec"],
                "flow_bytes_per_sec": flow["bytes_per_sec"],
            }

            node_records.append(record)

    return node_records


def extract_features(records):
    """
    Extract the two flow features used by the AI model.
    """

    return [
        [
            record["flow_packets_per_sec"],
            record["flow_bytes_per_sec"],
        ]
        for record in records
    ]


if __name__ == "__main__":
    records = build_flow_node_records()

    print("Total flow-node records:", len(records))

    features = extract_features(records)

    print("Feature vectors:", len(features))

    if features:
        print("First feature vector:", features[0])
