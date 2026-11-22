# AI Dataset Doctor

**Analyze. Detect. Clean. Understand your image datasets.**

AI Dataset Doctor is an image dataset quality analysis and cleaning tool designed to identify common problems in image datasets before they are used for machine learning or deep learning.

It combines traditional computer vision techniques with embedding-based visual analysis to detect potential dataset issues, generate reports, and help users organize problematic images.

## Features

AI Dataset Doctor currently supports six analysis modules:

| Analyzer | What it detects | Technology |
|---|---|---|
| Corruption Detection | Unreadable, invalid or corrupted image files | Pillow |
| Exact Duplicate Detection | Images with identical file contents | SHA-256 |
| Blur Detection | Images with insufficient sharpness | OpenCV, Variance of Laplacian |
| Resolution Detection | Images below configured minimum dimensions | Pillow |
| Visual Clustering | Groups images based on visual characteristics | Image embeddings |
| Label Validation | Potential inconsistencies between image content and assigned labels | Image embeddings |

### Additional capabilities

- Configurable analysis settings.
- Independent control over visual clustering.
- Flag or quarantine actions for detected issues.
- Non-destructive dataset handling.
- Clean dataset export.
- Structured JSON reports.
- Batch processing and parallel execution infrastructure.

## How It Works

The general workflow is:

```text
       Input Image Dataset
                |
                v
         Dataset Parsing
                |
                v
        Image Quality Checks
                |
                v
       Embedding Generation
                |
                v
     Visual Analysis & Validation
                |
                v
         Findings Generated
                |
                v
         Action Policy
          /          \
         v            v
       Flag       Quarantine
          \          /
           v        v
          Clean Dataset
                |
                v
           JSON Report
```

The system separates issue detection from the action taken on an image. This allows users to review findings without automatically deleting their original files.

## Supported Dataset Structures

AI Dataset Doctor supports the following dataset layouts.

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

### 3. Train / Validation / Test Dataset

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

### Supported Image Formats

- JPG / JPEG
- PNG
- BMP
- WEBP
- TIFF / TIF

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/namannsinha/AI-Dataset-Doctor
cd AI-Dataset-Doctor
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate the environment

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage

### Option 1: Streamlit Interface

Launch the application:

```bash
streamlit run frontend.py
```

Open the local URL displayed in your terminal.

Use the interface to select your dataset, configure analysis options, choose actions, and run the analysis.

### Option 2: Python CLI

You can also run the backend directly:

```bash
python run_dataset_doctor.py
```

The default dataset and output locations are:

```text
data/
├── input/
│   └── practice_dataset/
└── output/
```

The backend also supports specifying custom dataset and output paths through its `main()` function.

## Understanding the Results

### 1. Flag

Flagging records a detected issue without removing the image from the active dataset.

This is useful when you want to inspect findings before making changes.

### 2. Quarantine

Quarantining removes an affected image from the active working dataset and places a copy in the quarantine output.

The original input dataset is not directly modified.

### 3. Clean Dataset

The `Clean/` directory contains the images remaining in the active working dataset after the configured actions have been applied.

### 4. Visual Clusters

The `clusters/` directory contains images grouped according to their visual embeddings.

These groups can help users explore similarities and identify unusual samples.

### 5. JSON Report

The generated `report.json` contains structured analysis results, including:

- Analyzer name
- Number of images checked
- Detected findings
- Image identifiers
- Issue types
- Severity
- Explanations
- Values and thresholds, where applicable

## Output Structure

A typical execution can generate the following output:

```text
data/output/
├── Clean/
│   └── ...
│
├── Quarantine/
│   └── ...
│
├── clusters/
│   ├── cluster_0/
│   ├── cluster_1/
│   └── ...
│
├── embeddings/
│   ├── embeddings.npy
│   └── metadata.npz
│
└── report.json
```

The exact contents depend on the enabled analysis modules and the findings generated during execution.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Image Processing | Pillow, OpenCV |
| Numerical Computing | NumPy |
| Machine Learning | Scikit-learn |
| Visual Embeddings | Sentence Transformers / embedding models |
| Reporting | JSON |
| Testing | Pytest |

## Important Notes & Limitations

AI Dataset Doctor is an analysis and assistance tool. Its findings should be reviewed before making dataset-cleaning decisions.

- Blur detection depends on a configurable threshold.
- Exact duplicate detection identifies identical file contents; it does not automatically detect every visually similar image.
- Visual outliers are not necessarily incorrect images.
- Embedding-based label validation identifies potential inconsistencies, not guaranteed annotation errors.
- Near-duplicate detection and comprehensive train/test leakage detection are not currently presented as completed features.
- Very large datasets may require additional hardware resources and performance tuning.

## Project Roadmap

### Version 1 — Image Dataset Quality

- [x] Dataset parsing
- [x] Corruption detection
- [x] Exact duplicate detection
- [x] Blur detection
- [x] Resolution detection
- [x] Visual clustering
- [x] Visual outlier detection
- [x] Embedding-based label validation
- [x] Flag and quarantine actions
- [x] Clean dataset export
- [x] JSON reporting
- [x] Streamlit interface

### Future Improvements

- Near-duplicate detection
- Train/test leakage analysis
- Advanced dataset statistics
- Improved label validation
- Dataset health scoring
- More detailed reporting
- Interactive visual inspection
- Performance improvements for large datasets

## Project Structure

```text
AI-Dataset-Doctor/
│
├── app/
│   ├── analyzers/
│   ├── clean/
│   ├── core/
│   ├── embeddings/
│   ├── models/
│   ├── parsers/
│   ├── quarantine/
│   └── reports/
│
├── data/
│   ├── input/
│   └── output/
│
├── tests/
│
├── frontend.py
├── run_dataset_doctor.py
├── requirements.txt
└── README.md
```

## Running Tests

Run the complete test suite:

```bash
pytest
```

Run individual test modules when needed:

```bash
pytest tests/test_clustering.py
pytest tests/test_label_validation.py
```

## Core Philosophy

AI Dataset Doctor follows six principles:

1. **Detect before modifying** — Identify issues before taking action.
2. **Preserve original data** — Avoid permanently deleting user files.
3. **Use the right technique** — Apply traditional algorithms where appropriate and machine learning where visual understanding is useful.
4. **Keep components modular** — Each analyzer has a distinct responsibility.
5. **Make findings explainable** — Provide reasons behind detected issues.
6. **Support scalable processing** — Use batching and parallel processing infrastructure.

---

**AI Dataset Doctor — An automated quality-assurance layer between raw image datasets and machine learning pipelines.**