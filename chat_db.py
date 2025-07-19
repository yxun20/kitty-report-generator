import pandas as pd
import numpy as np

# 파일 경로
input_path = "./replace_dataset_output.csv"

# 데이터 불러오기
df = pd.read_csv(input_path)

# source -> id로 이름 변경 및 값 랜덤 할당 (0~10)
df.rename(columns={"source": "id"}, inplace=True)
df["id"] = np.random.randint(0, 11, size=len(df))

# 컬럼 이름 변경
column_rename_map = {
    "사전_유해성": "prior_harmfulness",
    "AI_유해성": "ai_harmfulness",
    "유해_단어": "harmful_words",
    "대체_제안형식": "replacement_format",
    "대체_문장": "replacement_text"
}
df.rename(columns=column_rename_map, inplace=True)

# 저장
output_path = "./chat_db.csv"
df.to_csv(output_path, index=False)
