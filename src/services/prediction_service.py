import joblib

class PredictionService:
    def __init__(self, model_path="models/sira_best_model.joblib", vectorizer_path="models/tfidf_vectorizer.joblib"):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

    def predict_single(self, raw_text: str) -> str:
        if not raw_text or not raw_text.strip():
            return "Unknown"
        
        # Transform unseen text using fitted vectorizer
        features = self.vectorizer.transform([raw_text])
        prediction = self.model.predict(features)
        return prediction[0]