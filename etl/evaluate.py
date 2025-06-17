#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import json
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def main(model_dir: str, data_dir: str, out_file: str):
    # Р·Р°РіСЂСѓР¶Р°РµРј
    with open(os.path.join(model_dir, 'model.pkl'), 'rb') as f:
        model = pickle.load(f)
    X_test = pd.read_csv(os.path.join(model_dir, 'X_test.csv'))
    y_test = pd.read_csv(os.path.join(model_dir, 'y_test.csv')).squeeze()

    # РїСЂРµРґСЃРєР°Р·Р°РЅРёСЏ Рё РјРµС‚СЂРёРєРё
    y_pred = model.predict(X_test)
    metrics = {
        'accuracy':  accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall':    recall_score(y_test, y_pred),
        'f1':        f1_score(y_test, y_pred)
    }

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Evaluate trained model")
    parser.add_argument('--model_dir', type=str, required=True, help="Directory with model and test data")
    parser.add_argument('--data_dir',  type=str, required=False, help="(РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ)")
    parser.add_argument('--out_file',  type=str, required=True, help="Path to save JSON metrics")
    args = parser.parse_args()
    main(args.model_dir, args.data_dir, args.out_file)
