import os
import sys
import pandas as pd

RAW_CSV_PATH = "site_db.csv"
AGG_CSV_PATH = "site_harmfulness_by_id.csv"

HARM_COLUMNS = ["abuse", "censure", "discrimination", "hate", "sexual", "violence"]

def load_and_aggregate() -> pd.DataFrame:
    if not os.path.isfile(RAW_CSV_PATH):
        print(f"Error: '{RAW_CSV_PATH}' 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(RAW_CSV_PATH)
    for col in ["id", "site"] + HARM_COLUMNS:
        if col not in df.columns:
            print(f"Error: '{col}' 컬럼이 없습니다.", file=sys.stderr)
            sys.exit(1)

    agg = df.groupby(["id", "site"], as_index=False)[HARM_COLUMNS].mean()
    agg.to_csv(AGG_CSV_PATH, index=False, encoding="utf-8")
    return agg

