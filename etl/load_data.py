#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import requests

def main(url: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()

    # в исходном файле нет заголовков
    columns = [
        'id', 'diagnosis',
        *(f'{stat}_{agg}' for agg in ['mean','se','worst'] for stat in [
            'radius','texture','perimeter','area','smoothness',
            'compactness','concavity','concave_points','symmetry','fractal_dimension'
        ])
    ]
    df = pd.read_csv(
        pd.compat.StringIO(response.text),
        header=None,
        names=columns
    )
    raw_path = os.path.join(out_dir, 'wdbc_raw.csv')
    df.to_csv(raw_path, index=False)
    print(f"Raw data saved to {raw_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Load WDBC data from UCI")
    parser.add_argument('--url',      type=str, required=True, help="URL to dataset")
    parser.add_argument('--out_dir',  type=str, required=True, help="Directory to save raw CSV")
    args = parser.parse_args()
    main(args.url, args.out_dir)
