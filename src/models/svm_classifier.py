from sklearn.svm import LinearSVC


class SVMClassifier:

    def __init__(self):
        self.model = LinearSVC()

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)