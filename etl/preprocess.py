#!/usr/bin/env python3
import os
import argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler

def main(in_dir: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(os.path.join(in_dir, 'wdbc_raw.csv'))

    # убираем id, переводим диагнозы в бинарный формат
    df = df.drop(columns=['id'])
    df['diagnosis'] = df['diagnosis'].map({'M':1, 'B':0})

    # разделяем на X и y
    y = df['diagnosis']
    X = df.drop(columns=['diagnosis'])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    df_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    df_scaled['diagnosis'] = y

    proc_path = os.path.join(out_dir, 'wdbc_processed.csv')
    df_scaled.to_csv(proc_path, index=False)
    print(f"Processed data saved to {proc_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Preprocess WDBC data")
    parser.add_argument('--in_dir',  type=str, required=True, help="Directory with raw CSV")
    parser.add_argument('--out_dir', type=str, required=True, help="Directory to save processed CSV")
    args = parser.parse_args()
    main(args.in_dir, args.out_dir)
