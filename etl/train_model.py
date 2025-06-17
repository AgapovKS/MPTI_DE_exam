#!/usr/bin/env python3
import os
import argparse
import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def main(data_dir: str, model_dir: str):
    os.makedirs(model_dir, exist_ok=True)
    df = pd.read_csv(os.path.join(data_dir, 'wdbc_processed.csv'))

    X = df.drop(columns=['diagnosis'])
    y = df['diagnosis']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # сохраняем модель и тестовый сэт
    with open(os.path.join(model_dir, 'model.pkl'), 'wb') as f:
        pickle.dump(model, f)
    X_test.to_csv(os.path.join(model_dir, 'X_test.csv'), index=False)
    y_test.to_csv(os.path.join(model_dir, 'y_test.csv'), index=False)
    print(f"Model and test split saved in {model_dir}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train LogisticRegression on WDBC")
    parser.add_argument('--data_dir', type=str, required=True, help="Processed data directory")
    parser.add_argument('--model_dir', type=str, required=True, help="Directory to save model and test data")
    args = parser.parse_args()
    main(args.data_dir, args.model_dir)
