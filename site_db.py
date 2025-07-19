import pandas as pd
import numpy as np
import os

CATEGORIES = ["abuse", "censure", "discrimination", "hate", "sexual", "violence"]

# STEP 1: replace_dataset.csv 불러오기
df = pd.read_csv("replace_dataset.csv")

# STEP 2: 지수분포 기반 랜덤값 생성 (중앙값이 약 0.2)
scale_param = 0.2 / np.log(2)  # ≈ 0.288
for cat in CATEGORIES:
    values = np.random.exponential(scale=scale_param, size=len(df))
    df[cat] = np.clip(values, 0, 1).round(4)

# STEP 3: temp 저장
df.to_csv("temp.csv", index=False)

# STEP 4: site_db 생성
chunk_size = 100
results = []

for i in range(0, len(df), chunk_size):
    chunk = df.iloc[i:i+chunk_size]
    avg_vector = chunk[CATEGORIES].mean().round(4).to_dict()
    dominant = max(avg_vector, key=avg_vector.get)
    rand_id = np.random.randint(1, 21)
    site = f"www.example{rand_id}.com"

    result = {
        "id": rand_id,
        "site": site,
        **avg_vector
    }
    results.append(result)

result_df = pd.DataFrame(results)
result_df.to_csv("site_db.csv", index=False)

# STEP 5: temp 삭제
if os.path.exists("temp.csv"):
    os.remove("temp.csv")
    print("temp.csv has been deleted.")

