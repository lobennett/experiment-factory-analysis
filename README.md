# Experiment Factory Analysis

> This repository contains scripts to fetch and export data by battery ID from the OG [Experiment Factory](https://www.expfactory.org/).

## Steps to run locally

### 1. Clone the Repository

Clone the project repository from GitHub to your local machine using the following command:

```sh
git clone https://github.com/lobennett/experiment-factory-analysis.git
```

### 2. Set Up the Environment File

Navigate into the cloned directory:

```sh
cd experiment-factory-analysis
```

Create an .env file to store private API tokens:

```sh
touch .env
```

Open this .env file in a text editor and add the following lines, replacing [token] with actual token values for Jaime and McKenzie:

```sh
JAIME_TOKEN=[token]
MCKENZIE_TOKEN=[token]
```

### 3. Create and Activate the Virtual Environment

```sh
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### 4. Execute the script to fetch data, specifying the battery ID using the --battery flag:

```sh
python src/fetch.py --battery [battery_id]
```

Note: To find the battery ID, look in the URL of the battery page. For example, if the URL is https://expfactory.org/batteries/254/, the battery ID is 254.

### 4. Finally, edit `preprocess_data` to handle the fetched data in whatever way you need
