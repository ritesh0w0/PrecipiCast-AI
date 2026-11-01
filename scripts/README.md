# Utility & Analysis Scripts

This directory contains standalone scripts used for model training, benchmarking, feature ranking, report updates, and visual asset generation:

| Script | Purpose |
| :--- | :--- |
| `train_extended_models.py` | Trains and benchmarks 7 distinct ML regressors (Decision Tree, Random Forest, XGBoost, Linear Regression, Ridge, Gradient Boosting, MLP) across historical 1995–2020 chronological partitions. |
| `generate_charts.py` | Generates publication-ready benchmark comparison (`assets/model_benchmark_comparison.png`) and feature importance charts (`assets/feature_importance.png`). |
| `generate_architecture.py` | Renders the comprehensive 5-tier architecture visual diagram (`assets/architecture_diagram.png`). |
| `generate_feature_ranking.py` | Analyzes Pearson correlation coefficients and exports top meteorological driver rankings. |
| `inspect_model.py` | Introspects serialized model objects, boosting trees, and scikit-learn/xgboost metadata. |
| `take_screenshots.py` | Spins up the Flask server and captures pixel-perfect UI dashboard screenshots via headless Chrome. |
| `update_report.py` | Automates docx table synchronization for research and academic project deliverables. |

