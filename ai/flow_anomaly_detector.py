from ai.flow_features import build_flow_node_records, extract_features
from ai.anomaly_detector import (
    split_train_validation_test,
    train_model,
    anomaly_scores,
    find_best_threshold,
    evaluate_predictions,
)


def main():
    print("\n=== SecureAI-Fabric Flow-Only Anomaly Detection ===")

    # Load flow-derived node records.
    records = build_flow_node_records()

    # Use the exact same experiment-level split as the
    # network-only detector.
    train_records, validation_records, test_records = (
        split_train_validation_test(records)
    )

    print(f"Total records: {len(records)}")
    print(f"Training records: {len(train_records)}")
    print(f"Validation records: {len(validation_records)}")
    print(f"Test records: {len(test_records)}")

    # Train only on NORMAL training samples.
    normal_train_records = [
        record
        for record in train_records
        if record["node_label"] == "normal"
    ]

    print(f"\nNormal training samples: {len(normal_train_records)}")

    # Extract the two flow features.
    train_features = extract_features(normal_train_records)
    validation_features = extract_features(validation_records)
    test_features = extract_features(test_records)

    # Train Isolation Forest.
    model = train_model(train_features)

    # Calibrate threshold using validation data.
    validation_scores = anomaly_scores(
        model,
        validation_features
    )

    validation_labels = [
        record["node_label"]
        for record in validation_records
    ]

    threshold, validation_metrics = find_best_threshold(
        validation_scores,
        validation_labels
    )

    print(f"Validation threshold: {threshold:.15f}")

    print("\n--- Validation ---")
    print(f"Precision: {validation_metrics['precision']:.4f}")
    print(f"Recall:    {validation_metrics['recall']:.4f}")
    print(f"F1:        {validation_metrics['f1']:.4f}")

    # Evaluate the frozen threshold on the test set.
    test_scores = anomaly_scores(
        model,
        test_features
    )

    test_labels = [
        record["node_label"]
        for record in test_records
    ]

    test_predictions = [
        "anomalous" if score >= threshold else "normal"
        for score in test_scores
    ]

    test_metrics = evaluate_predictions(
        test_labels,
        test_predictions
    )

    print("\n--- Test ---")
    print(f"TP: {test_metrics['tp']}")
    print(f"FP: {test_metrics['fp']}")
    print(f"TN: {test_metrics['tn']}")
    print(f"FN: {test_metrics['fn']}")
    print(f"Precision: {test_metrics['precision']:.4f}")
    print(f"Recall:    {test_metrics['recall']:.4f}")
    print(f"F1:        {test_metrics['f1']:.4f}")
    print(f"FPR:       {test_metrics['fpr']:.4f}")


if __name__ == "__main__":
    main()
