import sys
import pandas as pd
import argparse
import ast
import json
import os
from utils import fetch_data
from dotenv import load_dotenv


def preprocess_data(data: dict, outdir: str):
    """
    Preprocess fetched JSON data from the Experiment Factory results and save each
    experiment's results as a CSV file in the specified output directory.

    This is an example of how I might go about fetching and preprocessing data
    for the battery with ID 254. I wrote this pretty quickly so it might not be entirely
    robust, but it's just an example for getting started.

    """

    results = data.get("results", [])

    for res in results:
        worker_id = res.get("worker", {}).get("id", "unknown_worker")
        experiment_id = res.get("experiment", {}).get("exp_id", "unknown_experiment")
        experiment_data = res.get("data")

        if not experiment_data:
            continue

        print(f"\n### Processing: {worker_id} {experiment_id} ###")

        if isinstance(experiment_data, list):
            print("Note: Converting data format from list to dict")

            assert (
                len(experiment_data) == 1
            ), "More than one entries in Experiment Factory battery object."

            battery_data = experiment_data[0]
            trialdata = battery_data["trialdata"]
            df = pd.DataFrame(trialdata)

            filename = f"{worker_id}_{experiment_id}.csv"
            filepath = os.path.join(outdir, filename)
            df.to_csv(filepath, index=False)

            print(f"Task data saved to {filepath}")
        else:
            # I would check this for handling partially complete data
            print("Data not in list format, skipping.")
            pass


def main():
    """

    Fetch data from Experiment Factory by Battery ID. NOTE: You have to use either Jaime's or Mckenzie's
    access token depending on who made the battery.

    """

    outdir = "./out/"

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    parser = argparse.ArgumentParser(description="Select battery ID")
    parser.add_argument(
        "--battery",
        type=int,
        default=254,
        help="Battery ID to fetch, get this from Experiment Factory Battery URL.",
    )

    # Parse the arguments
    args = parser.parse_args()

    print("Fetching data from Experiment Factory")
    load_dotenv()

    for data in fetch_data(args.battery):
        preprocess_data(data, outdir)


if __name__ == "__main__":
    main()
