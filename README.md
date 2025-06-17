# Breast Cancer Wisconsin Diagnostic Pipeline

## ����������
1. [���� �������](#����-�������)  
2. [�������� ML-������](#��������-ml-������)  
3. [��������� �������](#���������-�������)  
4. [����������� � ����� ���������](#�����������-�-�����-���������)  
5. [��������� �������� ������](#���������-��������-������)  
    - ETL  
    - �������� � ������  
    - ����������� (MLOps)  
    - ���������� � �������� ����������  
6. [���������� �� �������](#����������-��-�������)  
7. [������ ������� � ������������](#������-�������-�-������������)  
8. [���� �� ���������](#����-��-���������)  

---

## ���� �������
- **����**: ��������� ��������������� ML-�������� ��� ������ �������� ������������� �������� �������� ������ (����������������� vs ���������������) �� ������ �������� WDBC.  
- **�������� ������**:  
  - �������� ���������� �� ����� ETL, �������� � ������;  
  - ������������� � ������� Airflow � retries � ������������;  
  - ���������� ���������� ������ � ������;  
  - ����������������� ������ ������� � ����������� �� ��������.

---

## �������� ML-������
- **��� ������**: �������� �������������.  
- **������� ��������**: F1-score (����� ������ precision/recall).  
- **������**: ����� �� 569 ��������, 30 ���������, ���� `diagnosis` (M=1, B=0).  
- **������**: ������������� ��������� (`sklearn.linear_model.LogisticRegression`).

---

## ��������� �������
```
breast_cancer_pipeline/
+-- dags/                     # Airflow DAG
�   L-- pipeline_dag.py
+-- etl/                      # ETL � ML-�������
�   +-- load_data.py
�   +-- preprocess.py
�   +-- train_model.py
�   L-- evaluate.py
+-- etl/data/                 
�   +-- raw/                  # ��������� ����� CSV
�   L-- processed/            # ��������������� CSV
+-- results/                  
�   +-- model/                # ���������� ������ � �������� �������
�   L-- metrics/              # JSON � ���������
+-- logs/                     # ���� Airflow
+-- config.yaml               # ��������� (����, URL, S3 � �.�.)
+-- requirements.txt          
L-- README.md                 # ��� ������������
```

---

## ����������� � ����� ���������

```mermaid
flowchart TD
    A[Load Data] --> B[Preprocess]
    B --> C[Train Model]
    C --> D[Evaluate]
    D --> E[Save Artifacts]
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#9ff,stroke:#333,stroke-width:2px
    style C fill:#ff9,stroke:#333,stroke-width:2px
    style D fill:#9f9,stroke:#333,stroke-width:2px
    style E fill:#f99,stroke:#333,stroke-width:2px
```

- **Load Data**: ��������� CSV �� URL.  
- **Preprocess**: ������� ID, �������� �����, ������������ ��������.  
- **Train Model**: ��������� ������, ������� LR, ��������� `model.pkl`, `X_test.csv`, `y_test.csv`.  
- **Evaluate**: ������� accuracy, precision, recall, F1 � ��������� � JSON.  
- **Save Artifacts**: �������� ����� � `results/`.

---

## ��������� �������� ������

### ETL
1. **load_data.py**  
   - ���������: `--url`, `--out_dir`  
   - ��������� wdbc.data, ����������� �������� �������� � ��������� `wdbc_raw.csv`.  
2. **preprocess.py**  
   - ���������: `--in_dir`, `--out_dir`  
   - ����������� `M/B > 1/0`, ������� `id`, ������������ �������� `StandardScaler`, ��������� `wdbc_processed.csv`.  

### �������� � ������
3. **train_model.py**  
   - ���������: `--data_dir`, `--model_dir`  
   - ����� �� train/test (80/20, stratify), ������� `LogisticRegression(max_iter=1000)`, ��������� ������ � �������� �������.  
4. **evaluate.py**  
   - ���������: `--model_dir`, `--out_file`  
   - ��������� ������ � `X_test`, `y_test`, ��������� ������� (`accuracy`, `precision`, `recall`, `f1`), ��������� JSON.

### ����������� (MLOps)
- **Airflow DAG** (`pipeline_dag.py`):
  - **Python/BashOperator** ��� ������� �������.
  - �����������: `load_data > preprocess > train_model > evaluate`.
  - `retries=2`, `retry_delay=5m`.
  - `schedule_interval='@daily'`, `catchup=False`.
  - ���� � `logs/breast_cancer_pipeline/...`.

### ���������� � �������� ����������
- �� ��������� ��������� �������� � `results/`.
- ��� S3 (�����������) � �������� � `config.yaml` ������ `s3:` � ������ �������� (`boto3`).

---

## ���������� �� �������

1. **������������ ���������**:
   ```bash
   cd /home/ksaga/DE/breast_cancer_pipeline/breast_cancer_pipeline
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **������ ������**:
   ```bash
   python etl/load_data.py --url <URL> --out_dir etl/data/raw
   python etl/preprocess.py --in_dir etl/data/raw --out_dir etl/data/processed
   python etl/train_model.py --data_dir etl/data/processed --model_dir results/model
   python etl/evaluate.py --model_dir results/model --out_file results/metrics/metrics.json
   ```
3. **Airflow**:
   ```bash
   export AIRFLOW_HOME=~/airflow
   export AIRFLOW__CORE__DAGS_FOLDER=<path_to>/dags
   export AIRFLOW__CORE__LOG_FOLDER=<path_to>/logs

   airflow db init
   airflow scheduler &
   airflow webserver -p 8080

   # ���� ������
   airflow tasks test breast_cancer_pipeline load_data 2025-06-17

   # ������� DAG
   airflow dags trigger breast_cancer_pipeline
   ```

---

## ������ ������� � ������������


| ����            | ��������� ������                               | ��������� / ������������                  |
|-----------------|-------------------------------------------------|-------------------------------------------|
| Load Data       | ���� ����������, 5xx/4xx                        | `response.raise_for_status()`, retry � Airflow |
| Preprocess      | ������������ ��������� CSV, NaN � ���������     | �������� ������� �������, `dropna()`      |
| Train Model     | ������ ����������������, ���������� �� ���������� | `max_iter=1000`, Stratified split, ����������� |
| Evaluate        | ������ `X_test`/`y_test`                        | �������� ������� �������, ������ exit      |
| Airflow DAG     | ����������� �������                             | `depends_on_past=False`, `catchup=False`  |
| S3 Upload (���.)| ��� ������� � AWS, �������� �����              | ������ �� `~/.aws/credentials`, ����������� |

---

## ���� �� ���������
- ������������ **MLflow** ��� �������� ������������� � �������.  
- ��������� �������: ROC-AUC, PR-AUC, ������������ �������.  
- �������� **Docker** � `docker-compose` ��� ���������.  
- ����������� �������������� **���-������** (FastAPI) ��� ������-������������.  
- ������������� ����������� (Slack/Email) �� �������� �� Airflow.  

---
