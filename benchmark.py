import time
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.models import (
    DecisionTreeIncidentClassifier,
    LogisticIncidentClassifier,
    NaiveBayesClassifier,
    RandomForestIncidentClassifier,
    SVMClassifier,
)

def run_benchmark():
    df = pd.read_csv("data/processed/incident_reports_clean.csv")
    
    X_raw = df["report_text"]
    y = df["incident_type"]

    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    X = vectorizer.fit_transform(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression (Baseline)": LogisticIncidentClassifier(),
        "Naive Bayes": NaiveBayesClassifier(),
        "Linear SVM": SVMClassifier(),
        "Decision Tree": DecisionTreeIncidentClassifier(),
        "Random Forest": RandomForestIncidentClassifier(),
    }

    results = []

    for name, model in models.items():
        # Time training phase
        start_train = time.perf_counter()
        model.train(X_train, y_train)
        train_time = round((time.perf_counter() - start_train) * 1000, 2)  # milliseconds

        # Time prediction phase
        start_pred = time.perf_counter()
        predictions = model.predict(X_test)
        pred_time = round((time.perf_counter() - start_pred) * 1000, 2)  # milliseconds

        results.append({
            "Model": name,
            "Accuracy": round(accuracy_score(y_test, predictions), 4),
            "Precision": round(precision_score(y_test, predictions, average="weighted", zero_division=0), 4),
            "Recall": round(recall_score(y_test, predictions, average="weighted", zero_division=0), 4),
            "F1 Score": round(f1_score(y_test, predictions, average="weighted", zero_division=0), 4),
            "Train Time (ms)": train_time,
            "Predict Time (ms)": pred_time,
        })

    results_df = pd.DataFrame(results).sort_values(by="F1 Score", ascending=False)
    
    print("\n" + "=" * 70)
    print("           SHELL NIGERIA - SIRA MODEL BENCHMARK REPORT")
    print("=" * 70)
    print(results_df.to_string(index=False))
    print("=" * 70 + "\n")

    # Bar chart visualization
    plt.figure(figsize=(10, 5))
    plt.bar(results_df["Model"], results_df["F1 Score"], color="#008080")
    plt.title("SIRA Incident Classifier Benchmark (F1-Score)")
    plt.xlabel("Model Architecture")
    plt.ylabel("Weighted F1 Score")
    plt.ylim(0, 1.0)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_benchmark()