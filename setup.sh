


# Create directories
mkdir -p data/raw data/processed data/external
mkdir notebooks
mkdir -p src/data src/models src/utils src/config
mkdir tests
mkdir scripts

# Create empty __init__.py files
touch src/__init__.py src/data/__init__.py src/models/__init__.py src/utils/__init__.py src/config/__init__.py
touch tests/__init__.py

# Create placeholder Python scripts
touch src/data/data_extraction.py src/data/data_processing.py
touch src/models/recommender.py src/models/evaluation.py
touch src/utils/helpers.py
touch src/config/config.yaml
touch tests/test_data_extraction.py tests/test_data_processing.py tests/test_recommender.py tests/test_evaluation.py
touch scripts/run_data_extraction.py scripts/run_training.py scripts/run_evaluation.py

# Create README.md
cat <<EOL > README.md
# Scientific Recommender System

## Project Structure

\`\`\`
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
\`\`\`

## Setup

Run the following command to set up the project:

\`\`\`bash
bash setup.sh
\`\`\`
EOL

# Create requirements.txt
cat <<EOL > requirements.txt
# Add your project dependencies here
numpy
pandas
scikit-learn
EOL

# Create setup.py
cat <<EOL > setup.py
from setuptools import setup, find_packages

setup(
    name="scientific_recommender",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
    ],
)
EOL

# Create .gitignore
cat <<EOL > .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule.*

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/
EOL

# Print completion message
echo "Project structure created successfully!"
