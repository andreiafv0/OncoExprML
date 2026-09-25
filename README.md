# OncoExprML

OncoExprML is a reproducible bioinformatics pipeline for analysing tumour samples using RNA-Seq gene expression profiles and Machine Learning.

The project uses a processed RNA-Seq dataset containing gene expression values from five cancer types:

- **BRCA**: Breast invasive carcinoma
- **KIRC**: Kidney renal clear cell carcinoma
- **COAD**: Colon adenocarcinoma
- **LUAD**: Lung adenocarcinoma
- **PRAD**: Prostate adenocarcinoma

The goal is not to detect whether a patient has cancer, but to analyse tumour samples already represented by RNA-Seq expression profiles. The workflow first explores whether tumour structure emerges without labels and then applies supervised classification to predict tumour type.

---

## Project Structure

```text
OncoExprML/
├── input/
│   ├── data.csv
│   └── labels.csv
├── output/
│   ├── figures/
│   ├── tables/
│   ├── final_model_kmeans_pca.joblib
│   ├── final_model_linear_svm.joblib
│   └── sample_prediction_report.md
├── notebooks/
│   └── rnaseq_cancer_classification.ipynb
├── src/
│   ├── run_pipeline.py
│   └── predict_sample.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Dataset

The input dataset contains:

- `data.csv`: RNA-Seq gene expression matrix.
- `labels.csv`: tumour class associated with each sample.

Each row corresponds to one tumour sample, and each column in `data.csv` corresponds to a gene expression feature.

The dataset contains:

- 801 samples
- 20,531 gene expression features
- 5 tumour classes

The features are labelled generically as `gene_0`, `gene_1`, ..., `gene_20530`. Since the dataset does not provide real gene symbols or biological identifiers, biological interpretation of individual features is limited.

---

## Main Workflow

The analysis follows two main computational stages.

First, an unsupervised analysis is performed:

1. Data loading and validation
2. Exploratory data analysis
3. Class distribution analysis
4. PCA visualization
5. PCA + K-Means clustering
6. Comparison between clusters and real tumour classes
7. ARI and NMI evaluation
8. Export of the unsupervised PCA + K-Means model

Then, a supervised analysis is performed:

1. Train/test split
2. Logistic Regression
3. Linear SVM
4. k-NN with PCA
5. Model comparison
6. Stratified cross-validation
7. Feature selection
8. Lightweight label-shuffling control in the notebook
9. Export of the final supervised Linear SVM model
10. Prediction example for an individual sample

The final unsupervised model was a PCA + K-Means pipeline selected based on ARI and NMI. The final supervised model was a Linear SVM, due to its high predictive performance and stability.

---

## Installation

To run the project locally, create a Python environment and install the required packages.

```bash
pip install -r requirements.txt
```

The required packages are listed in `requirements.txt`.

---

## Running the Pipeline Locally

To train and evaluate the final models, run:

```bash
python src/run_pipeline.py
```

This script:

- loads `input/data.csv` and `input/labels.csv`;
- validates the input data;
- evaluates different PCA + K-Means configurations;
- selects the best unsupervised clustering configuration;
- saves the unsupervised PCA + K-Means model;
- splits the dataset into training and test sets;
- trains the final supervised Linear SVM model;
- evaluates the supervised model;
- saves the supervised model and output tables;
- saves an approximate computational complexity analysis.

Generated outputs from `src/run_pipeline.py` include:

```text
output/
├── final_model_kmeans_pca.joblib
├── final_model_linear_svm.joblib
└── tables/
    ├── kmeans_pca_comparison.csv
    ├── final_kmeans_clustering_metrics.csv
    ├── final_kmeans_cluster_assignments.csv
    ├── final_kmeans_cluster_class_table.csv
    ├── final_model_metrics.csv
    ├── final_model_classification_report.csv
    ├── final_model_confusion_matrix.csv
    ├── top_selected_features.csv
    └── complexity_analysis.csv
```

Additional notebook-only outputs may include figures and the lightweight label-shuffling control files:

```text
output/
├── figures/
│   └── label_shuffle_control_svm.png
└── tables/
    ├── label_shuffle_control_results.csv
    └── label_shuffle_control_scores.csv
```

The label-shuffling control is kept in the notebook only and is not part of the automated `run_pipeline.py` script.

---

## Predicting One Sample

After training the models, an example analysis can be run with:

```bash
python src/predict_sample.py
```

A specific sample can also be selected:

```bash
python src/predict_sample.py sample_0
```

This script:

- loads the PCA + K-Means model, if available;
- assigns the sample to a K-Means cluster;
- reports the most frequent tumour class within that cluster;
- loads the trained Linear SVM model;
- predicts the tumour class of the selected sample;
- saves a Markdown report in `output/sample_prediction_report.md`.

Example output:

```text
A carregar dados e modelo supervisionado...
A carregar modelo não supervisionado PCA + K-Means...

Resultado da análise da amostra
-------------------------------
Amostra: sample_0

Modelo não supervisionado: PCA + K-Means
Cluster atribuído: 3
Classe mais frequente neste cluster: PRAD - Prostate adenocarcinoma / adenocarcinoma da próstata
Nota: o K-Means atribui clusters, não classes tumorais diretamente.

Modelo supervisionado: Linear SVM
Classe real: PRAD - Prostate adenocarcinoma / adenocarcinoma da próstata
Classe prevista: PRAD - Prostate adenocarcinoma / adenocarcinoma da próstata
Resultado supervisionado: classificação correta

Relatório guardado em: /app/output/sample_prediction_report.md
```

The K-Means cluster should not be interpreted as a direct tumour class prediction. K-Means is an unsupervised method and does not use class labels during clustering.

---

## Running with Docker

The project can also be executed inside a Docker container to improve reproducibility.

Build the Docker image:

```bash
docker build -t oncoexprml .
```

Run the full pipeline:

```bash
docker run --rm -v "$PWD/output:/app/output" oncoexprml
```

Run the prediction script for a specific sample:

```bash
docker run --rm -v "$PWD/output:/app/output" oncoexprml python src/predict_sample.py sample_0
```

When using WSL/Linux, the recommended command is:

```bash
docker run --rm -v "$PWD/output:/app/output" oncoexprml
```

On Windows PowerShell, the volume path may need to be written explicitly, for example:

```powershell
docker run --rm -v "C:/Users/beatc/Desktop/OncoExprML/output:/app/output" oncoexprml
```

---

## Using the Notebook

The full analysis is available in:

```text
notebooks/rnaseq_cancer_classification.ipynb
```

To run the notebook, select a Python kernel with the project dependencies installed.

If using a virtual environment, create it and install the dependencies:

```bash
python -m venv .venv
```

Activate the environment.

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

Then install the requirements:

```bash
pip install -r requirements.txt
```

To make the environment available as a Jupyter kernel:

```bash
python -m ipykernel install --user --name oncoexprml --display-name "Python (OncoExprML)"
```

Then, in VS Code or Jupyter, select:

```text
Python (OncoExprML)
```

This step is only necessary for running the notebook interactively. It is not required when running the scripts or Docker pipeline.

---

## Results Summary

The unsupervised PCA + K-Means analysis was performed first to evaluate whether tumour samples form natural groups based only on gene expression profiles, without using class labels during clustering. The best clustering configuration used 50 PCA components and achieved:

- ARI: 0.815
- NMI: 0.865

These results indicate that the RNA-Seq profiles contain relevant molecular structure, since the clusters show substantial correspondence with the real tumour classes. However, the clustering is not perfect, and some tumour types show partial overlap.

The supervised Linear SVM achieved strong performance on the test set, with high accuracy and F1-score macro. Stratified cross-validation confirmed that the supervised performance was stable across different data splits.

The feature selection analysis showed that high performance could be maintained even when using a reduced subset of features. This suggests that part of the discriminative signal between tumour types is concentrated in a subset of the expression profile.

A lightweight label-shuffling control was included in the notebook to compare the supervised performance obtained with real labels against performance obtained after shuffling the training labels. This is an exploratory sanity check, not a formal permutation test, and is not included in `run_pipeline.py`.

The pipeline also exports a ranking of the most discriminative anonymous expression features based on ANOVA F-scores. These features are kept as `gene_x` identifiers because the dataset does not provide real gene symbols or external gene IDs.

---

## Complexity Analysis

The pipeline includes an approximate computational complexity analysis saved in:

```text
output/tables/complexity_analysis.csv
```

This analysis summarizes the main preprocessing, unsupervised and supervised learning steps.

The notation used is:

- `n`: number of samples
- `p`: number of expression features
- `r`: number of PCA components
- `q`: number of K-Means clusters
- `c`: number of tumour classes
- `i`: number of algorithm iterations
- `F`: number of cross-validation folds

The main computational bottleneck is the high number of expression features (`p = 20531`). Standardization and feature selection scale linearly with the expression matrix size, while PCA introduces additional cost because it projects the original high-dimensional data into a smaller space. PCA is especially important before K-Means and k-NN, since both methods become less efficient and less stable in very high-dimensional spaces.

Cross-validation increases the computational cost because it repeats model training and evaluation across multiple folds. However, this step improves the reliability of the evaluation by testing model stability across different train/test partitions.

---

## Limitations

This project has several limitations:

- The dataset contains processed RNA-Seq expression values, not raw sequencing reads.
- The features are named generically as `gene_0`, `gene_1`, etc.
- No real gene symbols, Ensembl IDs or RefSeq identifiers are provided.
- The pipeline can identify discriminative expression features, but these cannot be directly mapped to specific biological genes without an external mapping file.
- The results should not be interpreted as clinical validation.
- The unsupervised PCA + K-Means model assigns clusters, not tumour diagnoses.
- The supervised pipeline classifies samples among five known tumour classes; it does not diagnose cancer presence or recommend treatment.

---

## Future Work

A future extension of this pipeline could use RNA-Seq datasets with real gene identifiers, such as harmonized TCGA/GDC expression data.

This would allow:

- mapping selected features to real genes;
- biological interpretation of discriminative genes;
- pathway or functional enrichment analysis;
- comparison of model-selected features with known cancer biomarkers;
- extension of the pipeline to other tumour types or datasets.

Another possible extension would be to support upstream RNA-Seq processing from FASTQ files. In that case, Biopython could be used for basic read inspection and quality summaries, while specialized RNA-Seq tools would still be required for alignment or quantification.

---

## Important Note

This project is intended for educational and computational bioinformatics purposes. It is not a clinical diagnostic tool.
