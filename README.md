# Microbiome-Cytokine-Interactions

# Decoding the Human Microbial-Immune Axis: A Multi-Site Atlas of Microbiome-Cytokine Interactions

[![GitHub license](https://img.shields.io/github/license/Sebukpor/Microbiome-Cytokine-Interactions)](https://github.com/Sebukpor/Microbiome-Cytokine-Interactions/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-brightgreen)](https://jupyter.org/)

## Overview

Welcome to the official repository for the pioneering study: **Decoding the Human Microbial-Immune Axis: A Multi-Site Atlas of Microbiome-Cytokine Interactions Reveals Novel Biomarkers and Therapeutic Avenues Across Health and Disease**.

This repository hosts the complete computational pipeline, datasets, and reproducible analyses for our integrative multi-omics study. I analyzed 642 deeply phenotyped human samples from four body sites (stool, mouth, nasal, and skin), integrating ~66 cytokine analytes (excluding controls CHEX1–CHEX4) with Kraken2-classified microbiome data (~234 features). Using advanced bioinformatics, multivariate statistics (PERMANOVA, PERMDISP), machine learning (Random Forest with SMOTE), and network science, I uncovered site-specific microbial-immune signatures classifying clinical states (Healthy, Infection, Immune perturbation [Imz], Metabolic [Weight-gain/Loss]) with up to 98% accuracy.

**Key insights**:
- **LEPTIN** as a universal cytokine hub, co-varying with site-specific consortia (e.g., *Paraprevotella* in mouth, *Labilibaculum* in nasal, *Salmonella* in stool).
- Nasal/oral microbiomes show strongest disease restructuring; gut/skin exhibit resilience.
- Temporal analyses reveal post-infection diversity erosion and immune-driven drifts, informing intervention windows.

This work establishes the first multi-ecosystem atlas of microbial-immune crosstalk, enabling non-invasive AI diagnostics and microbiome-targeted therapies in precision ecosystem medicine.

For the full manuscript:  
[![Full Paper PDF](https://img.shields.io/badge/PDF-Full%20Paper-red)](Decoding_the_Human_Microbial-Immune_Axis.pdf)

## Data Sources

The genomic data used in this study originates from the **Zindi MPEG-G Compression Challenge**, compressed MPEG-G files which were later decompressed to FASTQ for downstream task:

- **MPEG-G compressed genomic data**:  
  [Kaggle Dataset: maestroalert/trainfiles](https://www.kaggle.com/datasets/maestroalert/trainfiles)

- **Decompressed FASTQ files**:  
  [Kaggle Dataset: divinesebukpor/trainfiles](https://www.kaggle.com/datasets/divinesebukpor/trainfiles)

These datasets were processed as part of the MPEG-G decompression and taxonomic classification pipeline described in this repository.

## Repository Contents

This repo is structured for easy reproducibility, with Jupyter notebooks as the primary workflow tools and raw/processed data files.

- **Notebooks** (Core Analysis Pipeline):
  - [`Decompressing mpegg files to fastq.ipynb`](Decompressing_mpegg_files_to_fastq.ipynb): MPEG-G decompression of compressed genomic data to FASTQ format.
  - [`Taxanomic classification of fastq files with Kraken and Bracken.ipynb`](Taxanomic_classification_of_fastq_files_with_Kranken_and_Bracken.ipynb): Taxonomic profiling of FASTQ files using Kraken2 and Bracken for abundance estimation (note: "Kranken" is a playful nod to Kraken!).
  - [`cytokine_profiles_microbiome_merging.ipynb`](cytokine_profiles_microbiome_merging.ipynb): Merging cytokine profiles with microbiome data for integrated analysis.
  - [`Cytokine_Microbiome_Analysis.ipynb`](Cytokine_Microbiome_Analysis.ipynb): End-to-end analysis including t-SNE visualization, PERMANOVA, Random Forest classification, network analysis, and temporal Shannon diversity plotting.

- **Data** (Anonymized & Processed):
  - [`cytokine_profiles.csv`](cytokine_profiles.csv): High-resolution cytokine measurements (~66 analytes) across samples.
  - [`Train.csv`](Train.csv): Merged IDs of training dataset for microbiome, cytokines, and metadata.
  - [`Train_Subjects.csv`](Train_Subjects.csv): Subject-level metadata.

- **Other**:
  - [`LICENSE`](LICENSE): Apache-2.0 license.
  - This [`README.md`](README.md): You're reading it!

> **Note**: Raw human genomic data is processed (MPEG-G compressed); for full raw access, contact the author. All analyses use centered log-ratio (CLR) transformations for compositional data handling.

## Quick Start

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/Sebukpor/Microbiome-Cytokine-Interactions.git
   cd Microbiome-Cytokine-Interactions
   ```

2. **Set Up Environment** (Python 3.8+ with Jupyter):
   - Install dependencies via conda/pip (key packages: pandas, numpy, scikit-learn, matplotlib, seaborn, networkx):
     ```bash
     pip install pandas numpy scikit-learn matplotlib seaborn jupyter notebook
     # For Kraken2/Bracken: Follow official install instructions (not via pip; requires database download)
     ```
   - Launch Jupyter:
     ```bash
     jupyter notebook
     ```

3. **Run the Pipeline**:
   - Open and execute notebooks sequentially:  
     **Decompression → Taxonomic classification → Merging → Full analysis**.
   - Example: In `Cytokine_Microbiome_Analysis.ipynb`, run cells to reproduce t-SNE clusters (Figure 1) or temporal diversity plots (Figure 2).

> For containerized runs: A [Dockerfile](Dockerfile) can be added upon request. Notebooks are also compatible with Google Colab.

## Usage Examples

- **Generate Figures**: Run the analysis notebook to reproduce t-SNE clusters or Shannon diversity line plots by health status/site.
- **Train Classifiers**: Use Random Forest sections for custom health state prediction:
  ```python
  rf_model = RandomForestClassifier()
  rf_model.fit(X_train, y_train)
  ```
- **Extend Analysis**: Modify notebooks for new sites or features—e.g., integrate metagenomic functional profiling.


## Contributing & Contact

Contributions welcome! Fork, submit PRs, or open issues for bugs/features.  
For collaborations, data access, or questions: **divinesebukpor@gmail.com**

Licensed under [Apache-2.0](LICENSE).  
⭐ Star this repo if it fuels your microbiome research!

---

*Empowering precision medicine through microbial-immune insights.*
