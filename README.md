# Experiment Factory Analysis

> This repository contains a script to fetch and export data by battery ID from Experiment Factory.

## Usage

Clone the repository

```bash
git clone https://github.com/lobennett/experiment-factory-analysis.git
```

Navigate to repository

```bash
cd /path/to/experiment-factory-analysis
```

Create a `.env` file and add your API tokens:

```bash
cp .env.example .env
```

Run the `fetch.py` script

```bash
uv run fetch.py --battery-ids "216 217 218"
```
