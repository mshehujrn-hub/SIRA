## SIRA Model Benchmarking & Evaluation Report

### 1. Performance Benchmark Results

| Model Architecture | Accuracy | Precision | Recall | F1 Score | Train Time (ms) | Predict Time (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 14.28 | 0.66 |
| **Naive Bayes** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 3.22 | 0.17 |
| **Linear SVM** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11.69 | 0.27 |
| **Decision Tree** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9.29 | 0.45 |
| **Random Forest** | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 115.87 | 4.97 |

---

### 2. Baseline Model & Technical Justification

#### Baseline Model Selection
**Logistic Regression** served as the baseline model. In high-dimensional text classification using TF-IDF vectorization, simple linear models establish a robust benchmark for linear separability before considering complex ensemble methods.

#### Production Deployment Recommendation
**Linear SVM** is recommended for production deployment within the Shell Nigeria SIRA pipeline.

#### Key Justifications

* **Sub-Millisecond Inference Latency:** Linear SVM processes inference requests in **0.27 ms**—over **18x faster** than Random Forest (4.97 ms). This ultra-low latency makes it ideal for real-time incident report processing in production systems.
* **Sparse Matrix Optimization:** TF-IDF feature matrices generate thousands of sparse dimensions. Linear SVM naturally optimizes maximum-margin decision boundaries across sparse vectors without risking overfitting.
* **Resource Efficiency & Maintainability:** Compared to tree ensemble models like Random Forest, Linear SVM has a significantly smaller memory footprint, fast training execution (11.69 ms), and lower compute overhead for production updates.