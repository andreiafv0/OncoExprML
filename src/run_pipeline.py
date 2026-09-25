# 1. Imports

from pathlib import Path

import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from sklearn.feature_selection import SelectKBest, f_classif, VarianceThreshold


# 2. Define main project paths

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_DIR / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
TABLES_DIR = OUTPUT_DIR / "tables"


# 3. Ensure output folders exist

OUTPUT_DIR.mkdir(exist_ok=True)
TABLES_DIR.mkdir(exist_ok=True)


# 4. Define input file paths

data_path = INPUT_DIR / "data.csv"
labels_path = INPUT_DIR / "labels.csv"


# 5. Check whether input files exist

if not data_path.exists():
    raise FileNotFoundError("data.csv was not found in the input folder.")

if not labels_path.exists():
    raise FileNotFoundError("labels.csv was not found in the input folder.")


# 6. Load data

print("Loading data...")

data = pd.read_csv(data_path, index_col=0)
labels = pd.read_csv(labels_path, index_col=0)


# 7. Validate data

print("Validating data...")

same_samples = data.index.equals(labels.index)

if not same_samples:
    print("Error: samples in data.csv and labels.csv are not in the same order.")
    raise ValueError("Sample IDs are not aligned.")

has_class_column = "Class" in labels.columns

if not has_class_column:
    print("Error: labels.csv does not contain a column named 'Class'.")
    raise ValueError("The 'Class' column was not found in labels.csv.")

missing_values_data = data.isna().sum().sum()

if missing_values_data > 0:
    print("Error: missing values were found in data.csv.")
    print("Number of missing values:", missing_values_data)
    raise ValueError("Missing values found in data.csv.")

missing_values_labels = labels.isna().sum().sum()

if missing_values_labels > 0:
    print("Error: missing values were found in labels.csv.")
    print("Number of missing values:", missing_values_labels)
    raise ValueError("Missing values found in labels.csv.")


# 8. Define features and target

X = data
y = labels["Class"]


# 9. Evaluate different PCA + K-Means configurations

print("Evaluating unsupervised PCA + K-Means model...")

pca_components_list = [10, 20, 50, 100]
clustering_results = []

for n_components in pca_components_list:

    clustering_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("pca", PCA(
            n_components=n_components,
            svd_solver="randomized",
            random_state=42
        )),
        ("kmeans", KMeans(
            n_clusters=5,
            random_state=42,
            n_init=20
        ))
    ])

    clusters = clustering_pipeline.fit_predict(X)

    ari = adjusted_rand_score(y, clusters)
    nmi = normalized_mutual_info_score(y, clusters)

    clustering_results.append({
        "PCA components": n_components,
        "ARI": ari,
        "NMI": nmi
    })

clustering_results_df = pd.DataFrame(clustering_results)

clustering_results_df.to_csv(
    TABLES_DIR / "kmeans_pca_comparison.csv",
    index=False
)


# 10. Select the best unsupervised configuration

best_clustering_config = clustering_results_df.sort_values(
    by="ARI",
    ascending=False
).iloc[0]

best_pca_components = int(best_clustering_config["PCA components"])

print("Best K-Means configuration:")
print("PCA components:", best_pca_components)
print("ARI:", best_clustering_config["ARI"])
print("NMI:", best_clustering_config["NMI"])


# 11. Train the final unsupervised model

final_clustering_pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(
        n_components=best_pca_components,
        svd_solver="randomized",
        random_state=42
    )),
    ("kmeans", KMeans(
        n_clusters=5,
        random_state=42,
        n_init=20
    ))
])

final_clusters = final_clustering_pipeline.fit_predict(X)


# 12. Save the final unsupervised model

clustering_model_path = OUTPUT_DIR / "final_model_kmeans_pca.joblib"

joblib.dump(final_clustering_pipeline, clustering_model_path)


# 13. Save cluster assignments for each sample

final_cluster_assignments = pd.DataFrame({
    "Sample": X.index,
    "True class": y.values,
    "Cluster": final_clusters
})

final_cluster_assignments.to_csv(
    TABLES_DIR / "final_kmeans_cluster_assignments.csv",
    index=False
)


# 14. Save cluster vs true class table

final_cluster_class_table = pd.crosstab(
    final_cluster_assignments["Cluster"],
    final_cluster_assignments["True class"]
)

final_cluster_class_table.to_csv(
    TABLES_DIR / "final_kmeans_cluster_class_table.csv"
)


# 15. Save final clustering metrics

final_clustering_metrics = pd.DataFrame([{
    "Best PCA components": best_pca_components,
    "ARI": best_clustering_config["ARI"],
    "NMI": best_clustering_config["NMI"],
    "Number of clusters": 5
}])

final_clustering_metrics.to_csv(
    TABLES_DIR / "final_kmeans_clustering_metrics.csv",
    index=False
)


# 16. Split data into training and test sets

print("Splitting data into training and test sets...")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 17. Create final supervised model

model = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel="linear", random_state=42))
])


# 18. Train model

print("Training Linear SVM model...")

model.fit(X_train, y_train)


# 19. Predict test set

print("Evaluating supervised model...")

y_pred = model.predict(X_test)


# 20. Calculate metrics

metrics = {
    "Accuracy": accuracy_score(y_test, y_pred),
    "Precision macro": precision_score(y_test, y_pred, average="macro"),
    "Recall macro": recall_score(y_test, y_pred, average="macro"),
    "F1-score macro": f1_score(y_test, y_pred, average="macro")
}

metrics_df = pd.DataFrame([metrics])


# 21. Save main metrics

metrics_df.to_csv(
    TABLES_DIR / "final_model_metrics.csv",
    index=False
)


# 22. Save classification report

report = classification_report(
    y_test,
    y_pred,
    output_dict=True
)

report_df = pd.DataFrame(report).transpose()

report_df.to_csv(
    TABLES_DIR / "final_model_classification_report.csv"
)


# 23. Save confusion matrix

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=model.classes_
)

cm_df = pd.DataFrame(
    cm,
    index=[f"True_{label}" for label in model.classes_],
    columns=[f"Pred_{label}" for label in model.classes_]
)

cm_df.to_csv(
    TABLES_DIR / "final_model_confusion_matrix.csv"
)


# 24. Save final supervised model

model_path = OUTPUT_DIR / "final_model_linear_svm.joblib"

joblib.dump(model, model_path)


# 25. Rank the most discriminative anonymous features

print("Calculating ranking of the most discriminative anonymous features...")

top_feature_pipeline = Pipeline([
    ("variance", VarianceThreshold(threshold=0.0)),
    ("select", SelectKBest(score_func=f_classif, k=100))
])

top_feature_pipeline.fit(X_train, y_train)

variance_step = top_feature_pipeline.named_steps["variance"]
select_step = top_feature_pipeline.named_steps["select"]

features_after_variance = X_train.columns[variance_step.get_support()]
selected_features = features_after_variance[select_step.get_support()]
selected_scores = select_step.scores_[select_step.get_support()]

top_features_df = pd.DataFrame({
    "Feature": selected_features,
    "ANOVA F-score": selected_scores
}).sort_values(
    by="ANOVA F-score",
    ascending=False
)

top_features_df.to_csv(
    TABLES_DIR / "top_selected_features.csv",
    index=False
)


# 26. Save computational complexity analysis

print("Saving computational complexity analysis...")

n_samples, n_features = X.shape
n_classes = y.nunique()
n_clusters = 5
n_folds = 5

complexity_table = pd.DataFrame({
    "Step": [
        "Data validation",
        "Standardization",
        "PCA",
        "K-Means",
        "Logistic Regression",
        "Linear SVM",
        "k-NN training",
        "k-NN prediction",
        "SelectKBest ANOVA",
        "Cross-validation"
    ],
    "Approximate time complexity": [
        "O(n × p)",
        "O(n × p)",
        "O(n × p × r)",
        "O(i × n × q × r)",
        "O(i × n × p × c)",
        "Approximately O(n × p) to O(n² × p)",
        "O(n_train × r)",
        "O(n_test × n_train × r)",
        "O(n × p)",
        "O(F × model cost)"
    ],
    "Application in this project": [
        f"Validation of the matrix with {n_samples} samples and {n_features} features.",
        "Mean and standard deviation calculated for each expression feature.",
        f"Reduction from {n_features} features to principal components.",
        f"Clustering of samples into {n_clusters} clusters in PCA space.",
        f"Multiclass supervised baseline with {n_classes} classes.",
        "Final supervised model for tumour classification.",
        "Stores training samples after PCA reduction.",
        "Computes distances between test and training samples.",
        "Selects anonymous features with higher discriminative power.",
        f"Repeats training and evaluation across {n_folds} folds."
    ]
})

complexity_table.to_csv(
    TABLES_DIR / "complexity_analysis.csv",
    index=False
)


# 27. Show results in terminal

print("Pipeline completed successfully.")

print("Unsupervised model saved to:", clustering_model_path)
print("Unsupervised model metrics:")
print(final_clustering_metrics)

print("Supervised model saved to:", model_path)
print("Supervised model metrics:")
print(metrics_df)

print("Top 5 most discriminative anonymous features:")
print(top_features_df.head())
