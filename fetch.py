# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "python-dotenv",
#     "pandas",
# ]
# ///

import json
import logging
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import requests
from dotenv import load_dotenv

def fetch_data(url: str, access_token: str) -> pd.DataFrame:
    """
    Fetches pages of results from a paginated API endpoint and saves individual experiment data.

    Args:
        url: The initial URL to fetch data from (paginated API endpoint)
        access_token: The access token for authentication

    Returns:
        A pandas DataFrame containing all results metadata
    """
    headers = {"Authorization": f"token {access_token}"} if access_token else {}

    all_results = []
    page_count = 0
    
    while url:
        page_count += 1
        logger.info(f"Retrieving page {page_count}: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            break

        data = response.json()
        results = data.get("results", [])
        
        if not results:
            logger.warning(f"No results found on page {page_count}")
        
        for result in results:
            _save_experiment_data(result)
            
        all_results.extend(results)
        
        # Move to next page - this is the key fix
        next_url = data.get("next")
        if next_url != url:  # Prevent infinite loops on malformed APIs
            url = next_url
        else:
            logger.warning("Next URL same as current URL, stopping to prevent infinite loop")
            break

    logger.info(f"Total results gathered: {len(all_results)} across {page_count} pages")
    return pd.DataFrame(all_results)

def _save_experiment_data(result: Dict[str, Any]) -> None:
    """Save individual experiment data to CSV file."""
    experiment_id = _safe_get(result, ["experiment", "exp_id"], "unknown")
    battery_name = _safe_get(result, ["battery", "name"], "unknown")
    worker_id = _safe_get(result, ["worker", "id"], "unknown")
    finishtime = result.get("finishtime", "unknown")
    completed = result.get("completed", "unknown")
    experiment_data = result.get("data", [])
    
    if not experiment_data:
        logger.warning(f"No data found for worker {worker_id}, experiment {experiment_id}")
        return
    
    # Create output directory
    output_dir = Path("data") / f"worker-{worker_id}" / f"battery-{battery_name}" / f"experiment-{experiment_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save experiment data as JSON
    filename = f"worker-{worker_id}_experiment-{experiment_id}_battery-{battery_name}_finishtime-{finishtime}_completed-{completed}.json"
    output_file = output_dir / filename
    
    try:
        # Add metadata to the experiment data
        data_with_metadata = {
            'worker_id': worker_id,
            'experiment_id': experiment_id,
            'battery_name': battery_name,
            'finishtime': finishtime,
            'completed': completed,
            'data': experiment_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(data_with_metadata, f, indent=2, default=str)
        
        logger.info(f"Saved experiment data to {output_file}")
        
    except Exception as e:
        logger.error(f"Failed to save data to {output_file}: {e}")


def _safe_get(data: Dict[str, Any], keys: List[str], default: str = "NA") -> str:
    """Safely extract nested dictionary values."""
    try:
        result = data
        for key in keys:
            result = result[key]
        return str(result) if result is not None else default
    except (KeyError, TypeError, AttributeError):
        return default


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch paginated results from expfactory API for given battery IDs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--battery-ids",
        type=str,
        default="216",
        help="Space-delimited list of battery IDs to fetch results for"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./data",
        help="Output directory for results"
    )
    args = parser.parse_args()

    # Parse and validate battery IDs
    try:
        battery_ids = [int(bid.strip()) for bid in args.battery_ids.split() if bid.strip()]
        if not battery_ids:
            raise ValueError("No valid battery IDs provided")
    except ValueError as e:
        logger.error(f"Invalid battery IDs: {e}")
        return
    
    logger.info(f"Fetching data from expfactory for batteries: {battery_ids}")

    # Load environment variables
    load_dotenv()
    access_token = os.getenv("MCKENZIE_ACCESS_TOKEN")
    if not access_token:
        logger.error("MCKENZIE_ACCESS_TOKEN not found in environment variables")
        return

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each battery ID
    successful_batteries = []
    failed_batteries = []
    
    for battery_id in battery_ids:
        logger.info(f"Processing battery {battery_id}")
        
        url = f"http://expfactory.org/new_api/results/{battery_id}"
        
        try:
            results_df = fetch_data(url, access_token)
            
            if results_df.empty:
                logger.warning(f"No results found for battery {battery_id}")
                continue
                
            # Save metadata summary
            metadata_file = output_dir / f"battery_{battery_id}_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(results_df.to_dict('records'), f, indent=2, default=str)
            
            logger.info(f"Battery {battery_id}: processed {len(results_df)} results, metadata saved to {metadata_file}")
            successful_batteries.append(battery_id)
            
        except Exception as e:
            logger.error(f"Failed to process battery {battery_id}: {e}")
            failed_batteries.append((battery_id, str(e)))
    
    # Summary report
    logger.info(f"Processing complete. Successful: {len(successful_batteries)}, Failed: {len(failed_batteries)}")
    if successful_batteries:
        logger.info(f"Successfully processed batteries: {successful_batteries}")
    if failed_batteries:
        logger.warning(f"Failed batteries: {[bid for bid, _ in failed_batteries]}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    main()
