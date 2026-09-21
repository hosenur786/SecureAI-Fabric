from sklearn.ensemble import IsolationForest
import json
from sklearn.model_selection import train_test_split

FEATURES = [
    "rx_packets_per_sec",
    "tx_packets_per_sec",
    "rx_bytes_per_sec",
    "tx_bytes_per_sec",
]


def load_dataset(file_path="data/network_experiments.jsonl"):
    """
    Load telemetry records from the JSONL dataset.

    Returns:
        A list of telemetry dictionaries.
    """

    records = []

    with open(file_path, "r") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def extract_features(records):
    """
    Extract the selected network telemetry features.

    Returns:
        A list of feature rows.
    """

    feature_rows = []

    for record in records:
        row = []

        for feature in FEATURES:
            row.append(record[feature])

        feature_rows.append(row)

    return feature_rows


def train_model(normal_features):
    """
    Train an Isolation Forest model using normal telemetry samples.

    Returns:
        A trained Isolation Forest model.
    """

    model = IsolationForest(
        n_estimators=100,
        contamination="auto",
        random_state=42
    )

    model.fit(normal_features)

    return model


def predict(model, features):
    """
    Predict whether telemetry samples are normal or anomalous.

    Returns:
        A list of predictions.
        1  = normal
       -1  = anomaly
    """

    return model.predict(features)


def get_normal_features(records):
    """
    Extract feature rows from records labeled as normal.

    Returns:
        Feature rows belonging to normal telemetry samples.
    """

    normal_records = [
        record
        for record in records
        if record["node_label"] == "normal"
    ]

    return extract_features(normal_records)


def split_by_experiment(records, test_size=0.25, random_state=42):
    """
    Split telemetry records into training and testing sets
    while keeping all nodes from the same experiment together.

    Returns:
        Training records and testing records.
    """

    experiment_ids = sorted(
        set(record["experiment_id"] for record in records)
    )

    train_ids, test_ids = train_test_split(
        experiment_ids,
        test_size=test_size,
        random_state=random_state
    )

    train_ids = set(train_ids)
    test_ids = set(test_ids)

    train_records = [
        record
        for record in records
        if record["experiment_id"] in train_ids
    ]

    test_records = [
        record
        for record in records
        if record["experiment_id"] in test_ids
    ]

    return train_records, test_records
