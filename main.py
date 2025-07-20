from fastapi import FastAPI, HTTPException, Header, Depends, status
from pydantic import BaseModel
import pandas as pd
import os
import re
import json
from typing import List, Dict, Optional

from chat_data_manager import append_chat_data, get_user_harmful_chat_count, get_user_harmful_chat_data, ProcessedTextRequest
from quiz_generator import QuizGenerator
from chat_statistics import generate_chat_statistics
from report_generator import ReportGenerator

app = FastAPI()

# Initialize generators
quiz_gen = QuizGenerator()
report_gen = ReportGenerator()

# --- API Key Authentication ---
API_KEY = os.getenv("X_API_KEY")

async def verify_api_key(x_api_key: str = Header(...)):
    if not API_KEY:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="API Key not configured on server.")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key

# --- API Endpoint ---
@app.post("/process_chat_data", dependencies=[Depends(verify_api_key)])
async def process_chat_data(request: ProcessedTextRequest):
    append_chat_data(request)
    
    user_harmful_count = get_user_harmful_chat_count(request.user_id)
    
    response_message = f"Chat data logged for user {request.user_id}. Harmful count: {user_harmful_count}."
    quiz_results = []
    report_results = {}

    if user_harmful_count >= 10:
        print(f"User {request.user_id} has accumulated 10 or more harmful entries. Triggering quiz and report generation.")
        user_data = get_user_harmful_chat_data(request.user_id)
        
        # Generate quiz
        quiz_results = quiz_gen.generate_quizzes_from_data(user_data)
        
        # Generate statistics
        chat_stats = generate_chat_statistics(user_data)
        
        # Generate report
        report_results = report_gen.generate_report(chat_stats)
        
        response_message += " Quiz and report generation triggered."
        
    return {
        "message": response_message,
        "quiz_results": quiz_results,
        "report_results": report_results
    }