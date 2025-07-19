import pandas as pd

def get_harmful_chat_categories_by_id(target_id: int):
    """
    주어진 CSV 파일에서 특정 id에 대해 0보다 큰 유해성 카테고리 이름을 리스트로 반환합니다.

    Parameters:
        csv_path (str): CSV 파일 경로
        target_id (int): 조회하고자 하는 id 값

    Returns:
        List[str]: 유해성이 감지된 컬럼명 리스트 (0보다 큰 항목들)
    """
    # CSV 로드
    CSV_PATH = "~/kitty/report-generator/chat_harmfulness_by_id.csv"
    df = pd.read_csv(CSV_PATH)

    # 해당 ID의 row 찾기
    row = df[df["id"] == target_id]

    if row.empty:
        return []

    # ID 열 제외한 유해성 평균 열만 추출
    row_data = row.drop(columns=["id"]).iloc[0]

    # 0보다 큰 값의 컬럼명을 리스트로 반환
    harmful_categories = [col for col, val in row_data.items() if val > 0]

    return harmful_categories

