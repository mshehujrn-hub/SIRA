from sklearn.ensemble import RandomForestClassifier

class RandomForestIncidentClassifier:
    def __init__(self, random_state=42):
        self.model = RandomForestClassifier(random_state=random_state)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)