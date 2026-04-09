"""
Model evaluation pipeline.
"""


def evaluate_model(model_path: str, test_data_path: str) -> dict:
    """
    Evaluate a trained model on test data.
    Returns: {"accuracy": float, "precision": float, "recall": float, "f1": float}
    """
    pass


def generate_report(metrics: dict, output_path: str):
    """Generate an evaluation report."""
    pass


if __name__ == "__main__":
    metrics = evaluate_model("../models/sentiment_model.pkl", "../data/processed/")
    print(f"Model metrics: {metrics}")
