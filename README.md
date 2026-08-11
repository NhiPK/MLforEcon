# MLforEcon

Link of data for model development: https://drive.google.com/file/d/1RWvs2uHDCk_CmdLL2rByLhMTn8TudKRy/view?usp=sharing


**Objective**
The primary goal of this project is to forecast next-period firm-level credit demand growth (`ncliGrowthNextYear`)—serving as a proxy for unobservable direct loan demand—using an extensive panel of balance-sheet fundamentals, macroeconomic surveys, and textual sentiment indicators. Specifically, this study seeks to answer:
1. How responsive is firms’ credit demand to expectations about the economy?
2. Can text-based sentiment indicators from public reports improve forecasts?
3. Does this predictive value vary across different firm characteristics?

**Methodology**
*   **Algorithms:** We evaluated three machine learning approaches: XGBoost, Random Forest, and a Multi-Layer Perceptron (MLP) Neural Network.
*   **Information Blocks:** Features were evaluated incrementally across three nested sets: (1) Firm Fundamentals only, (2) Firm + Survey, and (3) Firm + Survey + Text.
*   **Validation Design:** The out-of-sample testing framework is designed to be highly conservative. Following a rolling-origin cross-validation on pre-2020 development data, everything from 2020 to 2023 was strictly held out. This placed the COVID-19 shock entirely out of sample to stress-test how the models generalize to unprecedented macroeconomic regimes.

## Directory Guide: Data Processing & Models

The project is organized into distinct directories to clearly separate data preparation from model training. Below is a detailed guide:

### 1. `data_processing/` Directory
All files used for cleaning and transforming raw data are located in this folder. It includes three main notebooks:
*   `firm_data_process.ipynb`: Processes accounting variables, financial ratios, and performs firm-level data cleaning.
*   `macro_data_process.ipynb`: Calculates and transforms macroeconomic expectation indicators.
*   `text_data_process.ipynb`: Processes textual data to extract sentiment indicators.

### 2. `model/` Directory
This folder contains the entire Machine Learning pipeline. The files are organized as follows:
*   **Initial Setup:**
    *   `model_setup.ipynb`: Contains shared configurations for Train/Test splitting (time-aware split) and Cross-Validation folds.
*   **Model Training:**
    *   `xgboost_model.ipynb`: Builds and performs hyperparameter tuning for the XGBoost model.
    *   `random_forest_model.ipynb`: Builds and performs hyperparameter tuning for the Random Forest model.
    *   `neural_network_model.ipynb`: Builds and performs hyperparameter tuning for the Neural Network (MLP).
*   **Evaluation & Synthesis:**
    *   `model_comparison.ipynb`: Compares the performance of the three trained models and analyzes Feature Importance.
    *   `combined_model.ipynb`: Contains ensemble model analysis.
*   **`outputs/` Subdirectory:** 
    *   Stores the exported evaluation results.