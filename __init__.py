# src/__init__.py
from .chat_module import get_harmful_chat_categories_by_id
from .site_module import get_harmful_site_categories_by_id
from .quiz_pipeline import HarmfulContentPipeline
from .append_to_chat_csv import append_row_to_chat_csv
from .append_to_site_csv import append_row_to_site_csv
from .site_aggregator import load_and_aggregate
from .site_statistics import build_user_stats
from .site_prompt_engine import generate_user_report
from .chat_generator import generate_chat_report

__all__ = [
    "get_harmful_chat_categories_by_id",
    "get_harmful_site_categories_by_id",
    "HarmfulContentPipeline",
    "append_row_to_chat_csv",
    "append_row_to_site_csv",
    "load_and_aggregate",
    "build_user_stats",
    "generate_user_report",
    "generate_chat_report",
]



    """
    1. "get_harmful_chat_categories_by_id" : 채팅에 대해서 ID 마다 6개 범주에 각 컬럼의 유해성 평균을 뽑아주는것
        입력 parameter : chat_id
        출력 parameter : { category_id: harmful_score }

    2. "get_harmful_site_categories_by_id" : 사이트에 대해서 ID 마다 6개 범주에 각 컬럼의 유해성 평균을 뽑아주는것
        입력 parameter : site_id
        출력 parameter : { category_id: harmful_score }

    3. "HarmfulContentPipeline" : 유해한 콘텐츠에 대한 전처리 및 필터링을 수행하는 파이프라인
        입력 parameter : content
        출력 parameter : { category_id: harmful_score }
        
    4. "append_row_to_chat_csv" : 채팅 데이터에 새로운 행을 추가하는 함수
        입력 parameter : row_data
        출력 parameter : None

    5. "append_row_to_site_csv" : 사이트 데이터에 새로운 행을 추가하는 함수
        입력 parameter : row_data
        출력 parameter : None

    6. "load_and_aggregate" : 데이터를 로드하고 집계하는 함수
        입력 parameter : None
        출력 parameter : aggregated_data

    7. "build_user_stats" : 사용자 통계 정보를 구축하는 함수
        입력 parameter : user_data
        출력 parameter : user_stats

    8. "generate_user_report" : 사용자 보고서를 생성하는 함수
        입력 parameter : user_stats
        출력 parameter : user_report
        
    9. "generate_chat_report" : 채팅 보고서를 생성하는 함수
        입력 parameter : chat_data
        출력 parameter : chat_report
    """