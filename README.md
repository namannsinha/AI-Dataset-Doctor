AI Dataset Doctor

AI Dataset Doctor is an image-dataset quality auditing and cleaning engine designed to identify dataset problems, explain findings, and safely prepare a cleaner dataset.

Current scope: Backend-only development. Frontend is postponed.

Project Vision

The long-term goal is to build a dataset "doctor" that can inspect an image dataset, identify quality and data problems, recommend actions, safely quarantine problematic files, and eventually use AI for semantic dataset analysis.

The system is intended to evolve from a local V1 tool into a scalable architecture capable of processing very large datasets.

Current V1 Scope

V1 focuses on image datasets.

Supported dataset structures

Flat

dataset/
├── image1.jpg
├── image2.jpg
└── image3.jpg

Class-separated

dataset/
├── cat/
│   ├── cat1.jpg
│   └── cat2.jpg
└── dog/
    ├── dog1.jpg
    └── dog2.jpg

Train/validation/test

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

Flat-dataset clustering is intentionally postponed to a future version.

Architecture Built So Far

Dataset
   │
   ▼
FolderParser
   │
   ▼
Dataset / ImageRecords
   │
   ▼
WorkingDataset
   │
   ▼
Pipeline
   │
   ├── Corruption Analyzer
   ├── Duplicate Analyzer
   ├── Blur Analyzer
   └── Resolution Analyzer
   │
   ▼
AnalysisResult / Findings
   │
   ▼
ActionPolicy
   ├── FLAG
   ├── QUARANTINE
   └── IGNORE
   │
   ▼
QuarantineManager
   │
   ▼
Updated WorkingDataset

Core architectural decisions

Analyzers detect problems; they do not directly delete or move files.

ActionPolicy decides whether a finding is flagged, quarantined, or ignored.

WorkingDataset represents the currently active dataset state.

The current V1 pipeline is sequential so quarantined images are unavailable to later analyzers.

The architecture is being reconsidered for batch-based and parallel processing before scaling to very large datasets.

Components Completed

1. Dataset Models

Core structured models include:

Dataset

ImageRecord

Finding

AnalysisResult

DatasetConfig

DatasetType

Action

quarantine-related records

ImageRecord stores information such as:

image ID

path

original path

filename

label

split

width

height

format

file size

2. Folder Parser

The FolderParser:

validates the dataset directory

recursively finds supported image files

detects dataset folder structure

extracts labels and train/validation/test splits

extracts image metadata

creates ImageRecord objects

creates the initial Dataset

Supported image extensions:

JPG
JPEG
PNG
BMP
WEBP
TIFF
TIF

The parser intentionally does not fail the entire dataset when an image cannot be opened. Such files can later be identified by the corruption analyzer.

3. WorkingDataset

WorkingDataset represents the currently active dataset state.
Example:

1000 images
   ↓
20 quarantined
   ↓
980 active images

The next analyzer works on the updated state.

4. Base Analyzer Architecture
All analyzers follow a common BaseAnalyzer interface.
Each analyzer provides:

a unique name
an analyze() method
standardized AnalysisResult output

This allows new analyzers to be added without rewriting the entire pipeline.

Analyzers Completed

5. Corruption Analyzer
Purpose: Detect images that cannot be correctly opened or verified.
Technology: Pillow

Image
  ↓
Pillow
  ↓
Open / Verify
  ↓
Valid or Corrupted

6. Exact Duplicate Analyzer
Purpose: Detect files with identical contents.
Technology: SHA-256 hashing
Example:

image1.jpg → HASH_A
image2.jpg → HASH_A
image3.jpg → HASH_B

image1.jpg and image2.jpg are exact duplicates.

Current limitation: SHA-256 does not detect visually identical images that were resized, recompressed, cropped, or otherwise modified. Near-duplicate detection is planned later.

7. Blur Analyzer
Purpose: Detect potentially blurry images.
Technology: OpenCV
Variance of Laplacian

Image
  ↓
Grayscale
  ↓
Laplacian
  ↓
Variance
  ↓
Blur / sharpness score

The threshold is configurable through DatasetConfig.

8. Resolution Analyzer
Purpose: Detect images below configured minimum width and height.
Example:
Minimum: 224 × 224

512 × 512 → Pass
224 × 224 → Pass
128 × 128 → Finding

It uses dimensions already extracted by the parser.

Action and Cleaning System

9. ActionPolicy
The user can decide what happens when an analyzer finds a problem:

FLAG
QUARANTINE
IGNORE

Example:

Duplicate → FLAG
Blur → QUARANTINE
Resolution → IGNORE

This separates detection from remediation.

10. QuarantineManager
Files are not permanently deleted.
When configured for quarantine, a file is moved to an issue-specific location:

output/
└── Quarantine/
    ├── corruption/
    ├── duplicate/
    ├── blur/
    └── resolution/

This makes cleaning reversible and allows inspection of removed files.

Pipeline
The current pipeline executes analyzers sequentially:

1000 images
    ↓
Corruption
    ↓
980 images
    ↓
Duplicate
    ↓
950 images
    ↓
Blur
    ↓
930 images
    ↓
Resolution

This was intentionally designed so quarantined images are removed from the active WorkingDataset before later analyzers run.

Testing
The project contains automated unit and integration tests.
Tests use controlled/synthetic data to verify known expected behavior.
For example:

image1 = duplicate
image2 = duplicate
image3 = unique

Expected:
1 duplicate finding

Tests cover:

parser behavior

dataset representation

WorkingDataset updates

analyzer behavior

findings

pipeline sequencing

FLAG behavior

QUARANTINE behavior

IGNORE behavior

physical quarantine operations

blur detection

resolution detection

duplicate detection

Automated tests answer:

"Does the implementation behave correctly according to the specification?"

Real datasets will later answer:

"Does the algorithm work effectively in real-world conditions?"

Both are required.

Scalability Architecture — Planned Revision

A scalability concern has been identified: users may eventually provide millions of images.

The current approach should therefore evolve from processing the entire dataset as one in-memory working object toward batch-based processing.

Planned direction

Dataset
   ↓
Parser
   ↓
Batch Manager
   ↓
Image Batches
   ↓
Parallel Independent Analyzers
   ↓
Findings
   ↓
Global / Dataset-level Analyzers
   ↓
Action Policy
   ↓
Quarantine / Final Dataset

Instead of:

1,000,000 images
       ↓
load everything

we want:

Batch 1 → 1000 images
Batch 2 → 1000 images
Batch 3 → 1000 images
...

Independent analyzers such as corruption, blur, and resolution can eventually run in parallel.

Global analyzers such as duplicate grouping, class statistics, leakage, and clustering require dataset-level state.

We should not introduce distributed systems such as Kafka/Kubernetes/etc. yet. First build a batch-based local architecture and make it parallel; distributed processing can be added later if justified.

Pending Work — V1

Dataset-level analysis

Dataset statistics

Class distribution

Class imbalance detection

Train/validation/test statistics

Image format statistics

Resolution statistics

Dataset summary

Leakage

Design leakage detection

Train/test similarity analysis

Near-duplicate detection

Leakage findings

Reporting

Final report model

JSON report

Human-readable report

Summary of findings

Quarantine summary

Dataset statistics

CLI

Dataset input command

Configuration options

Analyzer selection

Action policy configuration

Output directory configuration

Final report output

AI / ML Roadmap

AI will be used where semantic understanding is actually useful.

Traditional techniques

Corruption → Pillow
Exact duplicate → SHA-256
Blur → OpenCV
Resolution → Image metadata
Statistics → Statistical analysis

Future AI/ML

Image
  ↓
Vision Encoder
  ↓
Embedding
  ↓
Vector Index
  ├── Visual similarity
  ├── Near-duplicate detection
  ├── Train/test leakage
  ├── Wrong-label detection
  ├── Visual outlier detection
  └── Clustering

Future Versions

V1

Image dataset support

Dataset parsing

Corruption detection

Exact duplicate detection

Blur detection

Resolution detection

Dataset statistics

Leakage foundation

Quarantine

Reporting

CLI

V2

Potential additions:

Near-duplicate detection

Image embeddings

Wrong-label detection

Visual outlier detection

Flat dataset clustering

Stronger leakage detection

Adaptive thresholds

Improved dataset health analysis

Future

Potential product capabilities:

Dataset Health Score

Before/after comparison

AI explanations

AI remediation recommendations

Additional dataset formats

Frontend

Scalable workers

Cloud/object storage

Distributed processing

SaaS platform

Product Direction

The long-term goal is not simply:

"Find bad images."

The intended direction is:

Understand the health of an AI dataset, identify problems, explain them, recommend actions, safely apply approved changes, and verify the resulting dataset.

The eventual workflow:

Dataset
   ↓
Diagnose
   ↓
Explain
   ↓
Decide
   ↓
Quarantine / Flag
   ↓
Continue
   ↓
Report

Current Status

Foundation                  COMPLETE
Core image analyzers        COMPLETE
Dataset statistics          PENDING
Leakage                     PENDING
Reporting                   PENDING
CLI                         PENDING
AI subsystem                FUTURE PHASE
Frontend                    FUTURE PHASE
Scalable batch architecture IN DESIGN
Distributed processing      FUTURE

Immediate Next Step

Before adding many more analyzers, review and refactor the current pipeline toward:

BatchManager

Dataset metadata/state separate from loaded image data

Batch-local vs global analyzers

Parallel execution for independent analyzers

Safe action/quarantine handling

Then continue with dataset statistics.

Core Principle

Detect → Explain → Decide → Quarantine/Flag → Continue → Report