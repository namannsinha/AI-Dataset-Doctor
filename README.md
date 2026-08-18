# AI Dataset Doctor

AI Dataset Doctor is an intelligent image dataset quality analysis and cleaning tool.

It checks an image dataset for common problems, reports the findings, and can safely flag or quarantine problematic images based on user-defined actions.

The system combines traditional computer-vision techniques with AI/ML-based visual analysis where semantic understanding is required.

---

# Current Scope

The current project focuses on the **Image Dataset Pipeline**.

The backend is designed as a modular system so that different dataset-quality checks can be added independently.

## Supported Dataset Structures

### 1. Flat Dataset

```text
dataset/
├── image1.jpg
├── image2.jpg
└── image3.jpg
```

### 2. Class-Separated Dataset

```text
dataset/
├── cat/
│   ├── cat1.jpg
│   └── cat2.jpg
└── dog/
    ├── dog1.jpg
    └── dog2.jpg
```

### 3. Train/Test Dataset

```text
dataset/
├── train/
│   ├── cat/
│   └── dog/
├── val/
│   ├── cat/
│   └── dog/
└── test/
    ├── cat/
    └── dog/
```

Supported image formats include:

- JPG
- JPEG
- PNG
- BMP
- WEBP
- TIFF
- TIF

---

# What We Have Built

## Dataset Models

The project contains models for:

- Dataset
- ImageRecord
- Finding
- AnalysisResult
- DatasetConfig
- DatasetType
- Action
- ImageEmbedding
- ImageBatch

These models provide a common structure for communication between different components of the pipeline.

---

# Folder Parser

The folder parser:

- Validates the dataset path
- Finds supported image files recursively
- Detects dataset structure
- Detects classes
- Detects train/validation/test splits
- Reads image metadata
- Creates ImageRecord objects

The parser acts as the entry point for the image dataset.

```text
Dataset Folder
      ↓
Folder Parser
      ↓
Dataset
      ↓
Image Records
```

---

# Working Dataset

`WorkingDataset` keeps track of the images that are currently active during processing.

For example:

```text
1000 images
    ↓
20 images quarantined
    ↓
980 active images
```

The next processing step can operate on the updated dataset state.

This allows the pipeline to safely maintain the current state of the dataset without directly modifying the original files.

---

# Analyzer System

All analyzers follow a common `BaseAnalyzer` structure.

Currently implemented analyzers:

- Corruption Analyzer
- Exact Duplicate Analyzer
- Blur Analyzer
- Resolution Analyzer
- Visual Clustering Analyzer
- Label Validation Analyzer

Each analyzer has a specific responsibility and produces standardized findings.

The analyzers do not directly decide what should happen to an image.

Instead:

```text
Analyzer
   ↓
Finding
   ↓
Action Policy
   ↓
Action
```

This keeps detection and decision-making separate.

---

# Corruption Detection

The Corruption Analyzer uses Pillow to check whether images can be opened and processed correctly.

It can identify:

- Corrupted image files
- Invalid image files
- Unreadable images
- Images that cannot be decoded

---

# Exact Duplicate Detection

The Duplicate Analyzer detects exact duplicate images.

Exact duplicates are detected using SHA-256 file hashes.

Two files with the same content produce the same hash and are treated as exact duplicates.

For example:

```text
image1.jpg
image1_copy.jpg
another_name.jpg
```

can be detected as duplicates even when the filenames are different.

### Important

SHA-256 based duplicate detection identifies **exact duplicates**.

Near-duplicate detection, such as resized, compressed, or slightly modified versions, requires visual similarity techniques and is handled separately through the embedding-based system.

---

# Blur Detection

The Blur Analyzer uses OpenCV and the **Variance of Laplacian** method to estimate image sharpness.

A configurable threshold determines whether an image is considered too blurry.

Example:

```python
blur_threshold = 60.0
```

Images with sharpness below the configured threshold can be flagged.

---

# Resolution Detection

The Resolution Analyzer checks image width and height against configured minimum values.

Example:

```python
min_width = 224
min_height = 224
```

Images below the configured dimensions are reported as resolution issues.

---

# Image Embeddings

The project includes an embedding pipeline for higher-level visual analysis.

The embedding system converts an image into a numerical vector representation.

```text
Image
   ↓
Embedding Model
   ↓
Numerical Vector
   ↓
Embedding Store
```

Unlike exact hashing, embeddings allow the system to compare images based on their visual characteristics.

This enables analysis such as:

- Visual similarity
- Visual clustering
- Visual outlier detection
- Label validation
- Future near-duplicate detection

---

# Embedding Pipeline

The embedding functionality is separated into dedicated components:

```text
app/
└── embeddings/
    ├── embedding_pipeline.py
    ├── embedding_service.py
    └── embedding_store.py
```

Generated embeddings are stored under:

```text
data/output/embeddings/
```

Typical output:

```text
data/output/embeddings/
├── embeddings.npy
└── metadata.npz
```

The metadata maintains the relationship between embeddings, image IDs, and labels.

---

# Visual Clustering

The project includes visual clustering using the generated image embeddings.

The current implementation uses **DBSCAN** with cosine distance.

The workflow is:

```text
Images
   ↓
Embeddings
   ↓
DBSCAN
   ↓
Visual Groups
   ↓
Outlier Detection
```

The clustering analyzer is located at:

```text
app/analyzers/clustering.py
```

## Clustering Configuration

```python
cluster_eps = 0.15
cluster_min_samples = 3
enable_clustering = True
num_clusters = 5
```

Clustering can be enabled or disabled using:

```python
enable_clustering = True
```

or:

```python
enable_clustering = False
```

### Number of Clusters

The current implementation uses DBSCAN, so it does not require a fixed number of clusters. DBSCAN determines clusters using `cluster_eps` and `cluster_min_samples`.

The `num_clusters` setting is retained for future clustering algorithms that require a fixed number of clusters, such as K-Means.

---

# Visual Outlier Detection

DBSCAN assigns `-1` to samples that do not belong to a sufficiently dense cluster.

The system converts these samples into findings of type `visual_outlier`.

Example:

```text
Type: visual_outlier
Severity: medium
Reason: Image does not belong to any dense visual cluster.
```

Visual outliers can represent:

- Images from another dataset
- Incorrectly inserted images
- Unusual samples
- Potential annotation errors
- Images that differ significantly from the dataset distribution

---

# Label Validation

The project includes a Label Validation Analyzer.

The purpose is to identify images whose visual content may not agree with their assigned dataset labels.

```text
Image
   ↓
Visual Embedding
   ↓
Visual / Label Comparison
   ↓
Similarity Score
   ↓
Validation
   ↓
Potential Label Issue
```

Label validation is configured using:

```python
label_similarity_threshold = 0.75
label_margin = 0.03
```

This can help identify:

- Incorrect labels
- Misclassified images
- Annotation mistakes
- Ambiguous samples

---

# Action System

The user decides what happens when an issue is detected.

Available actions:

- FLAG
- QUARANTINE
- IGNORE

For example:

```text
Duplicate    → FLAG
Blur         → QUARANTINE
Resolution   → IGNORE
Clustering   → FLAG
```

Analyzers only create findings. They do not directly delete files.

The decision is handled through the `ActionPolicy`.

```text
Detection
    ↓
Decision
    ↓
Action
```

---

# Quarantine System

Images are not permanently deleted.

When the configured action is `QUARANTINE`, the image can be moved into a separate output directory.

Example:

```text
data/output/
└── quarantine/
    ├── corruption/
    ├── duplicate/
    ├── blur/
    └── resolution/
```

This allows users to review problematic images later and keeps dataset cleaning non-destructive.

---

# Clean Dataset Export

The Clean Dataset Manager exports the resulting working dataset.

Output:

```text
data/output/Clean/
```

The intended workflow is:

```text
Original Dataset
      ↓
Working Dataset
      ↓
Analysis
      ↓
Flag / Quarantine
      ↓
Remaining Active Images
      ↓
Clean Dataset
```

The original input dataset remains untouched.

---

# Current Pipeline

The image pipeline currently follows this general workflow:

```text
Dataset
   ↓
Folder Parser
   ↓
Working Dataset
   ↓
Configuration
   ↓
Action Policy
   ↓
Image Analyzers
   ├── Corruption
   ├── Resolution
   ├── Blur
   └── Duplicate
   ↓
Embedding Pipeline
   ↓
Embedding Store
   ↓
Visual Clustering
   ↓
Label Validation
   ↓
Clean Dataset
   ↓
JSON Report
```

---

# Current Pipeline Execution

The main execution script is:

```text
run_dataset_doctor.py
```

The current execution flow is approximately:

```text
1. Load dataset
        ↓
2. Parse dataset
        ↓
3. Create WorkingDataset
        ↓
4. Load DatasetConfig
        ↓
5. Create ActionPolicy
        ↓
6. Create analyzers
        ↓
7. Run Dataset Pipeline
        ↓
8. Generate embeddings
        ↓
9. Store embeddings
        ↓
10. Run visual clustering
        ↓
11. Run label validation
        ↓
12. Export clean dataset
        ↓
13. Generate report
        ↓
14. Display results
```

---

# Dataset Configuration

The main configuration is defined in:

```text
app/models/config.py
```

Current configuration includes:

```python
class DatasetConfig:

    blur_threshold: float = 60.0
    min_width: int = 224
    min_height: int = 224

    batch_size: int = 100
    worker_count: int = 4
    max_in_flight: int = 4

    label_similarity_threshold: float = 0.75
    label_margin: float = 0.03

    cluster_eps: float = 0.15
    cluster_min_samples: int = 3
    enable_clustering: bool = True
    num_clusters: int = 5
```

## Configuration Reference

| Configuration | Purpose |
|---|---|
| `blur_threshold` | Minimum acceptable image sharpness |
| `min_width` | Minimum image width |
| `min_height` | Minimum image height |
| `batch_size` | Number of images processed in a batch |
| `worker_count` | Number of workers available |
| `max_in_flight` | Maximum number of concurrent tasks |
| `label_similarity_threshold` | Similarity threshold used for label validation |
| `label_margin` | Confidence margin used for label validation |
| `cluster_eps` | DBSCAN neighborhood distance |
| `cluster_min_samples` | Minimum samples required to form a DBSCAN cluster |
| `enable_clustering` | Enables or disables visual clustering |
| `num_clusters` | Reserved for clustering algorithms that require a fixed number of clusters |

---

# Scalability

A major architectural concern identified during development is scalability.

A sequential pipeline works for smaller datasets, but users may eventually provide hundreds of thousands or millions of images.

The project therefore contains infrastructure for:

- Batch processing
- Worker-based processing
- Parallel execution
- Controlled in-flight work

The intended scalable architecture is:

```text
Dataset
   ↓
Parser
   ↓
Batch Manager
   ↓
Image Batches
   ↓
Worker Pool
   ↓
Parallel Processing
   ↓
Findings
   ↓
Global Analysis
   ↓
Action Policy
   ↓
Quarantine
   ↓
Report
```

For example:

```text
1,000,000 images

Batch 1 → 1,000 images
Batch 2 → 1,000 images
Batch 3 → 1,000 images
...
```

Independent operations such as corruption, blur, and resolution checks can eventually be parallelized. Operations requiring global dataset information, such as duplicate grouping and clustering, require coordination across batches.

---

# Batch Processing

The project contains batch-processing infrastructure under:

```text
app/core/
```

Important components include:

```text
batch_manager.py
worker.py
worker_pool.py
embedding_worker.py
hash_worker.py
```

The architecture can evolve from:

```text
Image 1 → Image 2 → Image 3 → Image 4
```

toward:

```text
             ┌── Worker 1
Batch ───────┼── Worker 2
             ├── Worker 3
             └── Worker 4
```

---

# Testing

Automated tests have been created for the core components.

Tests currently cover:

- Models
- Folder parser
- Working dataset
- Finding system
- Hashing
- Corruption analyzer
- Analyzer runner
- Action policy
- Quarantine
- Pipeline
- Blur analyzer
- Resolution analyzer
- Duplicate detection
- Embedding service
- Embedding pipeline
- Embedding store
- Embedding worker
- Visual clustering
- Label validation

Tests use controlled test data rather than relying only on real datasets.

Run the complete test suite:

```bash
pytest
```

Run clustering tests:

```bash
pytest tests/test_clustering.py
```

Run label validation tests:

```bash
pytest tests/test_label_validation.py
```

Real datasets can be used later for algorithm and performance validation.

---

# Reporting

The project generates structured analysis results that can be written to a JSON report.

Output:

```text
data/output/report.json
```

A report contains information such as:

- Analyzer name
- Images checked
- Issues found
- Image ID
- Issue type
- Severity
- Reason
- Value
- Threshold

Example:

```text
Analyzer: duplicate
Images checked: 32
Issues found: 18
```

The reporting layer provides machine-readable results for future interfaces and workflows.

---

# Output Structure

After running the pipeline, the output directory can contain:

```text
data/
└── output/
    ├── Clean/
    │   └── ...
    │
    ├── embeddings/
    │   ├── embeddings.npy
    │   └── metadata.npz
    │
    ├── quarantine/
    │   └── ...
    │
    └── report.json
```

---

# AI / ML Usage

AI is not used for every analyzer.

Traditional deterministic methods are used where they are more appropriate:

```text
Corruption       → Pillow
Exact duplicates → SHA-256
Blur             → OpenCV
Resolution       → Image metadata
```

AI/ML is introduced where visual or semantic understanding is useful.

Current and planned AI capabilities include:

- Image embeddings
- Visual similarity
- Visual clustering
- Visual outlier detection
- Label validation
- Near-duplicate detection
- Train/test leakage detection

General workflow:

```text
Image
   ↓
Vision Model
   ↓
Embedding
   ↓
Similarity / AI Analysis
```

This hybrid approach avoids using AI models for problems that can be solved more efficiently using traditional methods.

---

# Why Embeddings Are Important

Traditional duplicate detection answers:

> Are these two files exactly the same?

Embeddings allow the system to ask:

> Are these images visually similar?

For example:

```text
Image A
   ↓
Exact same file content
   ↓
Image B
```

can be detected using SHA-256.

However:

```text
Image A
   ↓
Resized / compressed / slightly modified
   ↓
Image B
```

may require visual embeddings and similarity analysis.

This provides a foundation for future near-duplicate detection.

---

# Planned Dataset Statistics

The next layer of image dataset analysis will provide statistical information such as:

- Total image count
- Number of classes
- Class distribution
- Class imbalance
- Image format distribution
- Resolution distribution
- Image size statistics
- Train/validation/test distribution

Example:

```text
Dataset
├── Total Images
├── Classes
├── Class Distribution
├── Resolution Statistics
├── Format Statistics
└── Split Statistics
```

---

# Planned Leakage Detection

Dataset leakage can occur when highly similar or duplicate samples appear across different dataset splits.

For example:

```text
Train
└── image_A.jpg

Test
└── image_A_copy.jpg
```

This can cause artificially high model performance.

Future leakage analysis will use:

```text
Exact Hashing
      +
Visual Similarity
      +
Dataset Split Information
```

to identify potential train/test leakage.

---

# Future Versions

## Version 1 — Image Dataset Quality

Focus on:

- Image dataset support
- Dataset parsing
- Corruption detection
- Exact duplicate detection
- Blur detection
- Resolution detection
- Dataset statistics
- Leakage foundation
- Quarantine
- Reporting
- CLI

The current image prototype has already progressed beyond the initial quality checks with embedding-based analysis.

## Version 2 — AI-Based Image Analysis

Planned/improved capabilities:

- Near-duplicate detection
- Improved image embeddings
- Visual similarity
- Wrong-label detection
- Visual outlier detection
- Flat dataset clustering
- Better train/test leakage detection
- Adaptive thresholds
- Improved cluster analysis

## Later Versions

Possible additions:

- Dataset Health Score
- Before/after comparison
- AI explanations
- AI recommendations
- More image formats
- Interactive dataset inspection
- Cloud storage
- Distributed processing

---

# Product Goal

The long-term goal is to make Dataset Doctor more than a collection of dataset checks.

The intended workflow is:

```text
Dataset
   ↓
Analyze
   ↓
Find Problems
   ↓
Explain Problems
   ↓
Recommend Actions
   ↓
Flag / Quarantine / Ignore
   ↓
Generate Clean Dataset
   ↓
Generate Report
```

The core principle is:

**Detect → Explain → Decide → Quarantine/Flag → Report**

---

# Current Status

## Completed

### Core Architecture

- [x] Dataset models
- [x] Folder parser
- [x] Working dataset
- [x] Analyzer architecture
- [x] Action policy
- [x] Quarantine system
- [x] Pipeline
- [x] Automated tests

### Image Quality Analysis

- [x] Corruption detection
- [x] Exact duplicate detection
- [x] Blur detection
- [x] Resolution detection

### AI/ML Analysis

- [x] Image embedding generation
- [x] Embedding storage
- [x] Visual clustering
- [x] Visual outlier detection
- [x] Clustering enable/disable
- [x] Label validation

### Output

- [x] Clean dataset export
- [x] JSON reporting

### Scalability Foundation

- [x] Batch processing infrastructure
- [x] Worker infrastructure
- [x] Embedding worker
- [x] Hash worker
- [x] Worker pool architecture

---

# Next Steps

The immediate development priorities are:

1. Improve dataset statistics
2. Implement train/test leakage analysis
3. Improve reporting
4. Strengthen label validation
5. Improve visual clustering controls
6. Improve batch and parallel processing
7. Build a user-facing interface after the backend is stable

---

# Technology Stack

### Language

```text
Python
```

### Computer Vision

```text
Pillow
OpenCV
```

### Machine Learning

```text
NumPy
Scikit-learn
Vision Embedding Models
```

### Testing

```text
Pytest
```

### Storage

```text
Filesystem
NumPy arrays
NPZ metadata
JSON reports
```

---

# Quick Start

## 1. Clone the repository

```bash
git clone <repository-url>
cd AI-Dataset-Doctor
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
```

## 3. Activate the environment

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\\Scripts\\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Add an image dataset

Place your dataset inside:

```text
data/input/
```

Example:

```text
data/input/practice_dataset/
├── image1.jpg
├── image2.jpg
├── image3.jpg
└── ...
```

## 6. Run Dataset Doctor

```bash
python3 run_dataset_doctor.py
```

---

# Example Output

A typical execution can produce:

```text
Loading dataset...
Dataset loaded: practice_dataset
Images found: 32

Running Dataset Doctor...

Generating embeddings...

Embeddings generated and stored for 32 images.

Running visual clustering...

Clustering checked 32 images.
Visual outliers found: 0

==================================================
DATASET DOCTOR RESULTS
==================================================

Analyzer: corruption
Images checked: 32
Issues found: 0

Analyzer: resolution
Images checked: 32
Issues found: 0

Analyzer: blur
Images checked: 32
Issues found: 0

Analyzer: duplicate
Images checked: 32
Issues found: 18

Analyzer: clustering
Images checked: 32
Issues found: 0

==================================================
Active images after analysis: 32
==================================================
```

---

# Project Philosophy

AI Dataset Doctor follows several important principles:

### 1. Detect Before Modifying

The system should identify problems before taking action.

### 2. Never Destroy Data Automatically

Problematic files should be flagged or quarantined rather than permanently deleted.

### 3. Use the Right Tool for the Problem

Not every problem requires AI.

```text
Simple Problem
      ↓
Traditional Algorithm

Complex Visual Problem
      ↓
AI / ML
```

### 4. Keep Components Independent

Each analyzer should have one clear responsibility.

### 5. Design for Scale

The architecture should eventually support very large datasets through batching, workers, and parallel processing.

### 6. Make Results Explainable

Every finding should provide a reason so that the user understands why an image was flagged.

---

# Project Structure

A simplified view of the current architecture:

```text
AI-Dataset-Doctor/
│
├── app/
│   ├── analyzers/
│   │   ├── base.py
│   │   ├── corruption.py
│   │   ├── duplicate.py
│   │   ├── blur.py
│   │   ├── resolution.py
│   │   ├── clustering.py
│   │   └── label_validation.py
│   │
│   ├── clean/
│   │   └── clean_dataset_manager.py
│   │
│   ├── core/
│   │   ├── action_policy.py
│   │   ├── batch_manager.py
│   │   ├── pipeline.py
│   │   ├── worker.py
│   │   ├── worker_pool.py
│   │   ├── embedding_worker.py
│   │   ├── hash_worker.py
│   │   └── working_dataset.py
│   │
│   ├── embeddings/
│   │   ├── embedding_pipeline.py
│   │   ├── embedding_service.py
│   │   └── embedding_store.py
│   │
│   ├── models/
│   │   ├── action.py
│   │   ├── analysis.py
│   │   ├── config.py
│   │   ├── dataset.py
│   │   ├── embedding_result.py
│   │   ├── finding.py
│   │   ├── image.py
│   │   └── ImageBatch.py
│   │
│   ├── parsers/
│   │   └── folder_parser.py
│   │
│   ├── quarantine/
│   │   └── quarantine_manager.py
│   │
│   └── reports/
│       └── report_writer.py
│
├── data/
│   ├── input/
│   └── output/
│       ├── Clean/
│       ├── embeddings/
│       ├── quarantine/
│       └── report.json
│
├── tests/
│
├── requirements.txt
├── README.md
└── run_dataset_doctor.py
```

---

# Final Goal

AI Dataset Doctor aims to become an automated quality-assurance layer between raw image datasets and machine-learning training pipelines.

```text
                 Raw Image Dataset
                       ↓
                AI Dataset Doctor
                       ↓
        ┌──────────────┴──────────────┐
        ↓                             ↓
     Good Data                  Problematic Data
        ↓                             ↓
 Clean Dataset                Flag / Quarantine
        │                             │
        └──────────────┬──────────────┘
                       ↓
                    Report
                       ↓
              ML Training Pipeline
```

The ultimate goal is to make image dataset quality assurance:

**Automated • Explainable • Safe • Scalable**
