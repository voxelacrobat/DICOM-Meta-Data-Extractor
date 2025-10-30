# DICOM-Meta-Data-Extractor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive tool for extracting, anonymizing, and analyzing DICOM metadata with advanced visualization and graph analysis capabilities.

## 📋 Overview

This tool consists of three main components:

1. **dcm_parser_cimage.py** - Class for DICOM handling and metadata extraction
2. **dcm_parser_main.py / dcm_parser_main_extended.py** - Main script for recursive parsing
3. **dcm_parser_analyzer.py** - Advanced analysis and visualization functions

## ⚠️ IMPORTANT NOTICE

**This tool is intended for research and development purposes only.**

- ❌ NOT for direct clinical use
- ❌ NOT approved for medical diagnosis
- ❌ NO certification as medical device
- ✅ ONLY for research, development, quality control

When using with patient data: Please comply with GDPR and local data protection regulations!

## 🚀 Features

### Core Functionality
- ✅ Recursive search through directory structures for DICOM files
- ✅ Extract all DICOM metadata into structured JSON format
- ✅ Optional: Anonymization while preserving folder structure
- ✅ Export to Excel (parsed_series.xlsx, patient_info.xlsx)

### Advanced Analysis
- 📊 **Statistical Analysis**
  - Number of patients, studies, series
  - Modality distribution
  - Manufacturer statistics
  - Institution analysis
  
- 🔍 **Duplicate Detection**
  - Finds potential duplicate examinations
  - Identifies same patients with identical date/modality
  
- 📈 **Visualizations**
  - Bar charts (modality distribution)
  - Pie charts (manufacturer shares)
  - Temporal trends
  - Heatmaps (modality × institution)
  - Interactive Sankey diagrams (patient → modality → manufacturer)
  
- 🕸️ **Graph Analysis**
  - Relationship graphs: Patient → Study → Series → Instance
  - Network metrics (degree, density, centrality)
  
- 🎯 **Clustering**
  - Modality × Manufacturer
  - Institution × Modality
  - Body Part × Modality

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Manager)

### Step 1: Clone Repository

```bash
git clone https://github.com/YourUsername/dicom-parser.git
cd dicom-parser
```

**Or download manually:**
- dcm_parser_cimage.py
- dcm_parser_main.py
- dcm_parser_main_extended.py
- dcm_parser_analyzer.py
- requirements.txt

### Step 2: Install Dependencies

**Option A: With virtualenv (recommended)**

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Direct installation**

```bash
pip install -r requirements.txt
```

**Required packages:**
- pydicom (DICOM handling)
- pandas (data analysis)
- numpy (numerical operations)
- matplotlib (basic visualization)
- seaborn (advanced visualization)
- networkx (graph analysis)
- plotly (interactive visualizations)
- openpyxl (Excel support)

## 📖 Usage

### Basic Usage (Parsing Only)

```python
from dcm_parser_main import parse_study_dirs

input_path = "C:\\path\\to\\dicom\\data"
output_path = "C:\\path\\to\\output"

# Without anonymization
parse_study_dirs(input_path, output_path, ananomize_dcm=False)
```

### Advanced Usage (Parsing + Analysis)

```python
from dcm_parser_main_extended import run_complete_analysis

input_path = "C:\\path\\to\\dicom\\data"
output_path = "C:\\path\\to\\output"

# Option 1: Parsing + Analysis (recommended)
run_complete_analysis(
    input_path=input_path,
    output_path=output_path,
    anonymize=False,
    run_analysis=True
)

# Option 2: Parsing + Anonymization + Analysis
run_complete_analysis(
    input_path=input_path,
    output_path=output_path,
    anonymize=True,
    run_analysis=True
)
```

### Standalone Analysis (on already parsed data)

```python
from dcm_parser_analyzer import DICOMMetadataAnalyzer

# Directory with already extracted JSON metadata
input_path = "C:\\path\\to\\dicom\\data"

# Initialize analyzer
analyzer = DICOMMetadataAnalyzer(input_path)

# Generate complete report
analyzer.generate_full_report(output_dir="./analysis_report")

# Or run individual analyses:
analyzer.load_metadata_files()
analyzer.create_dataframe()
analyzer.compute_basic_statistics()
analyzer.find_duplicate_studies()
analyzer.cluster_by_attributes()
analyzer.visualize_modality_distribution(output_path="./modality_dist.png")
```

## 📂 Output Structure

After execution, the following structure is created:

```
output_path/
│
├── parsed_series.xlsx              # Series overview
├── original_patient_info.xlsx      # Original patient data
├── ananomized_patient_info.xlsx    # Anonymized data (if enabled)
│
└── analysis_report/                # Analysis report (if enabled)
    ├── statistics.json             # Statistical metrics
    ├── complete_dataframe.csv      # Complete dataframe
    ├── duplicate_studies.csv       # Found duplicates
    │
    ├── cluster_modality_manufacturer.csv
    ├── cluster_institution_modality.csv
    ├── cluster_bodypart_modality.csv
    │
    ├── modality_distribution.png
    ├── manufacturer_pie.png
    ├── temporal_trend.png
    ├── heatmap_modality_institution.png
    └── sankey_patient_modality.html  # Interactive
```

## 🔧 Configuration

### Customizing Metadata Extraction

In `dcm_parser_cimage.py` you can customize extraction:

```python
# Example: Include private tags
metadata = orgDCM.extract_dicom_metadata(
    include_private=True,        # Private (manufacturer) tags
    include_pixel_data=False,    # PixelData field
    max_value_length=200         # Max length for values
)
```

### Customizing Visualizations

In `dcm_parser_analyzer.py` you can customize visualizations:

```python
# Example: Change number of top institutions in heatmap
def visualize_heatmap_modality_institution(self, output_path=None, top_n=15):
    # top_institutions = ... head(15)  # Instead of 10
    pass
```

## 📊 Example Analyses

### 1. Analyze Modality Distribution

```python
analyzer = DICOMMetadataAnalyzer("./data")
analyzer.load_metadata_files()
analyzer.create_dataframe()

stats = analyzer.compute_basic_statistics()
print(f"Found modalities: {stats['modalities']}")
```

**Output:**
```
Found modalities: {'CT': 1250, 'MR': 830, 'DX': 420, 'US': 180}
```

### 2. Find Duplicates

```python
duplicates = analyzer.find_duplicate_studies()
print(duplicates)
```

**Output:**
```
   PatientID  StudyDate Modality  Count
0  PAT123    20240115   CT        3
1  PAT456    20240120   MR        2
```

### 3. Visualize Temporal Trends

```python
analyzer.visualize_temporal_trend(output_path="./trend.png")
```

### 4. Perform Graph Analysis

```python
G = analyzer.create_relationship_graph()
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")
```

## 🔍 Advanced Features

### Set-Theoretic Operations

```python
# Patients with more than one modality
multi_modal_patients = analyzer.df.groupby('PatientID')['Modality'].nunique()
multi_modal_patients = multi_modal_patients[multi_modal_patients > 1]

print(f"Patients with multiple modalities: {len(multi_modal_patients)}")
```

### Custom Clustering

```python
# Example: Cluster by gender and modality
custom_cluster = analyzer.df.groupby(['PatientSex', 'Modality']).size()
print(custom_cluster)
```

### Temporal Queries

```python
# Studies in a specific time period
df_temp = analyzer.df.copy()
df_temp['StudyDate'] = pd.to_datetime(df_temp['StudyDate'], format='%Y%m%d')

studies_2024 = df_temp[df_temp['StudyDate'].dt.year == 2024]
print(f"Studies in 2024: {len(studies_2024)}")
```

## ⚠️ Important Notes

1. **Memory Usage**: For very large datasets (>10,000 DICOM files), memory consumption can be significant.

2. **Performance**: Graph analysis can take longer with large datasets.

3. **Anonymization**: Anonymization removes personal data but preserves medical structure.

4. **Private Tags**: Manufacturer-specific tags are extracted by default. This can be disabled.

## 🐛 Error Handling

The tool logs errors to `log.txt` in the input directory:

```
ERROR: C:\path\to\file.dcm
EXCEPTION: Tag (0010,0010) not found
```

## 📝 JSON Metadata Structure

Each DICOM file gets a `.json` file with the following structure:

```json
[
  {
    "path": "PatientName",
    "tag": "(0010,0010)",
    "group": 16,
    "element": 16,
    "vr": "PN",
    "name": "Patient's Name",
    "keyword": "PatientName",
    "value": "DOE^JOHN",
    "vm": 1,
    "private": false
  }
]
```

## 🔬 Scientific Applications

This tool is suitable for:

- 🏥 Quality control of medical image databases
- 📊 Retrospective study analyses
- 🔍 DICOM conformance testing
- 📈 Workflow optimization in radiology departments
- 🎓 Research data management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Summary:** You are free to use, modify, and distribute the code - even commercially. The only condition: The copyright notice must be retained.

## 👥 Authors & Credits

**M. Manzke**
- Original DICOM Parser (dcm_parser_cimage.py, dcm_parser_main.py)
- Concept, medical expertise & integration
- Metadata extraction (extract_dicom_metadata)

**Claude (Anthropic AI)**
- Analysis module (dcm_parser_analyzer.py)
- Visualizations & graph analysis

**Dependencies**
- pydicom, pandas, matplotlib, seaborn, networkx, plotly

---

**Version**: 1.1.0  
**Date**: October 30, 2025  
**Status**: Production Ready
