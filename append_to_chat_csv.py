import pandas as pd
import os

def append_row_to_chat_csv(new_data: dict):
    """
    기존 CSV 파일에 새 행을 추가합니다.
    
    Parameters:
        new_data (dict): 추가할 데이터 (key는 column명, value는 값)
    """
    # 파일이 존재하면 기존 데이터 불러오기
    CSV_PATH: "./chat_db.csv"
    if os.path.isfile(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

        # 컬럼 유효성 검사
        missing_cols = set(new_data.keys()) - set(df.columns)
        if missing_cols:
            raise ValueError(f"[ERROR] 존재하지 않는 컬럼: {missing_cols}")
    else:
        # 새 파일이면 데이터프레임 생성
        df = pd.DataFrame(columns=new_data.keys())

    # 행 추가
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # 저장
    df.to_csv(CSV_PATH, index=False)
    print(f"[INFO] 새 데이터가 '{CSV_PATH}'에 성공적으로 추가되었습니다.")

