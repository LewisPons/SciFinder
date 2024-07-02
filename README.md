# Scientific Recommender System

## Project Structure

```
scientific_recommender/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_extraction.py
│   │   └── data_processing.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── recommender.py
│   │   └── evaluation.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config/
│       ├── __init__.py
│       └── config.yaml
├── tests/
│   ├── __init__.py
│   ├── test_data_extraction.py
│   ├── test_data_processing.py
│   ├── test_recommender.py
│   └── test_evaluation.py
├── scripts/
│   ├── run_data_extraction.py
│   ├── run_training.py
│   └── run_evaluation.py
├── requirements.txt
├── setup.py
├── README.md
└── .gitignore
```

## Setup

Run the following command to set up the project:

```bash
bash setup.sh
```
