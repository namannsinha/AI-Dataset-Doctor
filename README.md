# AI Dataset Doctor

AI Dataset Doctor is an image dataset quality analysis and cleaning tool.

It checks an image dataset for common problems, reports the findings, and can safely quarantine problematic images based on user-defined actions.

## Current Scope

We are currently building the backend only.

Version 1 focuses on image datasets.

### Supported Dataset Structures

#### 1. Flat Dataset

```text
dataset/
├── image1.jpg
├── image2.jpg
└── image3.jpg
```

#### 2. Class-Separated Dataset

```text
dataset/
├── cat/
│   ├── cat1.jpg
│   └── cat2.jpg
└── dog/
    ├── dog1.jpg
    └── dog2.jpg
```

#### 3. Train/Test Dataset

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

Clustering of flat datasets is planned for a future version.

---

## What We Have Built

### Dataset Models

Created models for:

- Dataset
- ImageRecord
- Finding
- AnalysisResult
- DatasetConfig
- DatasetType
- Action

### Folder Parser

The folder parser:

- Validates the dataset path
- Finds supported image files recursively
- Detects dataset structure
- Detects classes
- Detects train/validation/test splits
- Reads image metadata
- Creates ImageRecord objects

Supported formats:

- JPG
- JPEG
- PNG
- BMP
- WEBP
- TIFF
- TIF

### Working Dataset

`WorkingDataset` keeps track of the images that are currently active.

Example:

```text
1000 images
   ↓
20 images quarantined
   ↓
980 active images
```

The next processing step works with the updated dataset state.

### Analyzer System

All analyzers follow a common `BaseAnalyzer` structure.

Currently implemented:

- Corruption Analyzer
- Exact Duplicate Analyzer
- Blur Analyzer
- Resolution Analyzer

### Corruption Detection

Uses Pillow to check whether images can be opened and processed correctly.

### Exact Duplicate Detection

Uses SHA-256 file hashes.

Two files with the same content produce the same hash and are treated as exact duplicates.

Near-duplicate detection is not implemented yet.

### Blur Detection

Uses OpenCV and the Variance of Laplacian method to estimate image sharpness.

### Resolution Detection

Checks image width and height against configured minimum values.

---

## Action System

The user decides what happens when an issue is detected.

Available actions:

- FLAG
- QUARANTINE
- IGNORE

For example:

```text
Duplicate → FLAG
Blur → QUARANTINE
Resolution → IGNORE
```

Analyzers only create findings. They do not directly delete files.

---

## Quarantine System

Images are not permanently deleted.

When the action is `QUARANTINE`, the image is moved into a separate folder based on the issue.

Example:

```text
output/
└── Quarantine/
    ├── corruption/
    ├── duplicate/
    ├── blur/
    └── resolution/
```

This allows the user to review removed images later.

---

## Current Pipeline

The current pipeline processes analyzers sequentially.

```text
Dataset
   ↓
Corruption
   ↓
Duplicate
   ↓
Blur
   ↓
Resolution
   ↓
Output
```

The important part is that quarantined images are removed from the active `WorkingDataset`, so later analyzers work on the remaining images.

---

## Testing

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
- Blur
- Resolution
- Duplicate detection

We use controlled test data instead of relying only on real datasets.

The purpose is to verify that each component behaves correctly and that changes do not break existing functionality.

Real datasets will be used later for algorithm validation.

---

# Scalability

A major architectural concern identified during development is scalability.

The current sequential pipeline works for smaller datasets, but users may eventually provide hundreds of thousands or millions of images.

We therefore plan to move toward:

```text
Dataset
   ↓
Parser
   ↓
Batch Manager
   ↓
Image Batches
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

Instead of loading and processing the entire dataset at once, images will be processed in batches.

For example:

```text
1,000,000 images

Batch 1 → 1,000 images
Batch 2 → 1,000 images
Batch 3 → 1,000 images
...
```

Independent analyzers such as corruption, blur, and resolution can eventually run in parallel.

Analyzers that need information from the complete dataset, such as duplicate grouping or dataset statistics, will use global state.

---

# Pending V1 Work

## Dataset Analysis

- [ ] Dataset statistics
- [ ] Class distribution
- [ ] Class imbalance
- [ ] Train/test statistics
- [ ] Image format statistics
- [ ] Resolution statistics

## Leakage

- [ ] Train/test leakage detection
- [ ] Similarity-based leakage detection
- [ ] Near-duplicate detection

## Reporting

- [ ] Report model
- [ ] JSON report
- [ ] Human-readable report
- [ ] Findings summary
- [ ] Quarantine summary
- [ ] Dataset summary

## CLI

- [ ] Dataset input
- [ ] Configuration options
- [ ] Analyzer selection
- [ ] Action selection
- [ ] Output directory
- [ ] Final report generation

---

# AI / ML Plans

AI will not be used for every analyzer.

Traditional methods will be used where they are more appropriate.

Examples:

```text
Corruption → Pillow
Exact duplicates → SHA-256
Blur → OpenCV
Resolution → Image metadata
Statistics → Statistical methods
```

AI/ML will be introduced for problems that require visual or semantic understanding.

Planned AI capabilities include:

- Image embeddings
- Near-duplicate detection
- Visual similarity
- Wrong-label detection
- Visual outlier detection
- Train/test leakage detection
- Clustering

Possible future flow:

```text
Image
   ↓
Vision Model
   ↓
Embedding
   ↓
Similarity / AI Analysis
```

---

# Future Versions

## Version 1

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

## Version 2

Possible additions:

- Near-duplicate detection
- Image embeddings
- Wrong-label detection
- Visual outlier detection
- Flat dataset clustering
- Better leakage detection
- Adaptive thresholds

## Later Versions

Possible additions:

- Dataset Health Score
- Before/after comparison
- AI explanations
- AI recommendations
- More dataset formats
- Frontend
- Batch workers
- Cloud storage
- Distributed processing
- SaaS platform

---

# Product Goal

The long-term goal is to make Dataset Doctor more than a collection of dataset checks.

The intended workflow is:

```text
Upload Dataset
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

Completed:

- Dataset models
- Folder parser
- Working dataset
- Analyzer architecture
- Corruption analyzer
- Duplicate analyzer
- Blur analyzer
- Resolution analyzer
- Action policy
- Quarantine system
- Pipeline
- Automated tests

Next:

1. Rework the architecture for batch processing and scalability
2. Add dataset statistics
3. Implement leakage analysis
4. Improve reporting
5. Build CLI
6. Add AI/ML capabilities in later stages

Frontend and SaaS development will come after the backend foundation is stable.
