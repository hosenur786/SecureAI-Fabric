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


def anomaly_scores(model, features):
    """
    Calculate anomaly scores for telemetry samples.

    Higher scores indicate more anomalous behavior.
    """

    return -model.score_samples(features)

def find_best_threshold(scores, labels):
    """
    Find the anomaly-score threshold that gives the best F1 score
    on the validation dataset.

    Args:
        scores: Anomaly scores for validation samples.
        labels: Actual labels ('normal' or 'anomalous').

    Returns:
        Best threshold and its evaluation metrics.
    """

    candidates = sorted(set(scores), reverse=True)

    best_threshold = None
    best_f1 = -1.0
    best_metrics = {}

    for threshold in candidates:
        predictions = [
            "anomalous" if score >= threshold else "normal"
            for score in scores
        ]

        tp = sum(
            1
            for actual, predicted in zip(labels, predictions)
            if actual == "anomalous" and predicted == "anomalous"
        )

        fp = sum(
            1
            for actual, predicted in zip(labels, predictions)
            if actual == "normal" and predicted == "anomalous"
        )

        tn = sum(
            1
            for actual, predicted in zip(labels, predictions)
            if actual == "normal" and predicted == "normal"
        )

        fn = sum(
            1
            for actual, predicted in zip(labels, predictions)
            if actual == "anomalous" and predicted == "normal"
        )

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold

            best_metrics = {
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }

    return best_threshold, best_metrics


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


def split_train_validation_test(records, random_state=42):
    """
    Split experiments into training, validation, and test sets.

    The split is stratified by scenario so that each set contains
    a balanced representation of the three network scenarios.

    Returns:
        Training records, validation records, and test records.
    """

    experiment_scenarios = {}

    for record in records:
        experiment_scenarios[record["experiment_id"]] = record["scenario"]

    experiment_ids = list(experiment_scenarios.keys())
    scenario_labels = [
        experiment_scenarios[experiment_id]
        for experiment_id in experiment_ids
    ]

    train_ids, temp_ids, train_labels, temp_labels = train_test_split(
        experiment_ids,
        scenario_labels,
        test_size=0.40,
        stratify=scenario_labels,
        random_state=random_state
    )

    validation_ids, test_ids = train_test_split(
        temp_ids,
        test_size=0.50,
        stratify=temp_labels,
        random_state=random_state
    )

    train_ids = set(train_ids)
    validation_ids = set(validation_ids)
    test_ids = set(test_ids)

    train_records = [
        record
        for record in records
        if record["experiment_id"] in train_ids
    ]

    validation_records = [
        record
        for record in records
        if record["experiment_id"] in validation_ids
    ]

    test_records = [
        record
        for record in records
        if record["experiment_id"] in test_ids
    ]

    return train_records, validation_records, test_records


def evaluate_predictions(actual, predicted):
    """
    Calculate classification metrics for anomaly detection.

    Args:
        actual: Actual labels.
        predicted: Model-predicted labels.

    Returns:
        A dictionary containing TP, FP, TN, FN,
        precision, recall, F1, and false-positive rate.
    """

    tp = sum(
        1
        for actual_label, predicted_label in zip(actual, predicted)
        if actual_label == "anomalous"
        and predicted_label == "anomalous"
    )

    fp = sum(
        1
        for actual_label, predicted_label in zip(actual, predicted)
        if actual_label == "normal"
        and predicted_label == "anomalous"
    )

    tn = sum(
        1
        for actual_label, predicted_label in zip(actual, predicted)
        if actual_label == "normal"
        and predicted_label == "normal"
    )

    fn = sum(
        1
        for actual_label, predicted_label in zip(actual, predicted)
        if actual_label == "anomalous"
        and predicted_label == "normal"
    )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    fpr = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
    }


def main():
    """
    Run the complete network anomaly detection baseline.
    """

    # Load the complete dataset.
    records = load_dataset()

    # Split experiments into training, validation, and test sets.
    train_records, validation_records, test_records = (
        split_train_validation_test(records)
    )

    # Use only normal training samples to train the detector.
    training_features = get_normal_features(train_records)

    model = train_model(training_features)

    # Generate anomaly scores for the validation set.
    validation_features = extract_features(validation_records)

    validation_scores = anomaly_scores(
        model,
        validation_features
    )

    validation_labels = [
        record["node_label"]
        for record in validation_records
    ]

    # Find the best threshold using validation data only.
    threshold, validation_metrics = find_best_threshold(
        validation_scores,
        validation_labels
    )

    # Evaluate the frozen threshold on the unseen test set.
    test_features = extract_features(test_records)

    test_scores = anomaly_scores(
        model,
        test_features
    )

    test_actual = [
        record["node_label"]
        for record in test_records
    ]

    test_predicted = [
        "anomalous" if score >= threshold else "normal"
        for score in test_scores
    ]

    test_metrics = evaluate_predictions(
        test_actual,
        test_predicted
    )

    print("\n=== SecureAI-Fabric Network Anomaly Detection ===")
    print(f"Total records: {len(records)}")
    print(f"Training records: {len(train_records)}")
    print(f"Validation records: {len(validation_records)}")
    print(f"Test records: {len(test_records)}")

    print(
        f"\nNormal training samples: "
        f"{len(training_features)}"
    )

    print(
        f"Validation threshold: "
        f"{threshold:.17g}"
    )

    print("\n--- Validation ---")
    print(
        f"Precision: {validation_metrics['precision']:.4f}"
    )
    print(
        f"Recall:    {validation_metrics['recall']:.4f}"
    )
    print(
        f"F1:        {validation_metrics['f1']:.4f}"
    )

    print("\n--- Test ---")
    print(f"TP: {test_metrics['tp']}")
    print(f"FP: {test_metrics['fp']}")
    print(f"TN: {test_metrics['tn']}")
    print(f"FN: {test_metrics['fn']}")

    print(
        f"Precision: {test_metrics['precision']:.4f}"
    )
    print(
        f"Recall:    {test_metrics['recall']:.4f}"
    )
    print(
        f"F1:        {test_metrics['f1']:.4f}"
    )
    print(
        f"FPR:       {test_metrics['fpr']:.4f}"
    )


if __name__ == "__main__":
    main()
