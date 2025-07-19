import pandas as pd

# 파일 경로
input_file = "./site_db.csv"
output_file = "./site_harmfulness_by_id.csv"

# CSV 읽기
df = pd.read_csv(input_file)

# 유해성 범주 컬럼 정의
harmful_columns = ["abuse", "censure", "discrimination", "hate", "sexual", "violence"]

# ID별로 평균 계산
grouped_df = df.groupby("id")[harmful_columns].mean().round(4).reset_index()

# 컬럼명 변경
grouped_df.columns = ["id"] + [f"mean_{col}" for col in harmful_columns]

# 저장
grouped_df.to_csv(output_file, index=False)
