import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from src.models import SVMClassifier

def train_and_persist():
    # Load dataset
    df = pd.read_csv("data/processed/incident_reports_clean.csv")
    
    # Fit vectorizer on full dataset
    vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
    X = vectorizer.fit_transform(df["report_text"])
    y = df["incident_type"]

    # Train best model (Linear SVM)
    best_model = SVMClassifier()
    best_model.train(X, y)

    # Ensure export directory exists
    os.makedirs("models", exist_ok=True)

    # Save artifacts
    joblib.dump(best_model, "models/sira_best_model.joblib")
    joblib.dump(vectorizer, "models/tfidf_vectorizer.joblib")
    
    print("Artifacts successfully saved to models/")

if __name__ == "__main__":
    train_and_persist()