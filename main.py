import os
import pandas as pd
import openai
import logging
import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Pydantic model for request body
class PromptRequest(BaseModel):
    prompt: str

# System Prompt for OpenAI and Claude
SYSTEM_PROMPT = "Write an essay for high school students, fully humanized."

# Word limit (approx. 180 words = ~500 tokens)
WORD_LIMIT_TOKENS = 500

@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}

# ✅ 1️⃣ API to Process a Single Prompt via Request Body (OpenAI)
@app.post("/process-openai")
async def process_openai_prompt(request: PromptRequest):
    """Process a single prompt using OpenAI GPT-3.5 Turbo with system prompt and word limit."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},  # System instruction
                {"role": "user", "content": request.prompt}
            ],
            max_tokens=WORD_LIMIT_TOKENS
        )
        return {"prompt": request.prompt, "response": response["choices"][0]["message"]["content"]}
    except Exception as e:
        logging.error(f"Error calling OpenAI: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating response from OpenAI")

# ✅ 2️⃣ API to Process a Single Prompt via Request Body (Claude 3.5)
@app.post("/process-claude")
async def process_claude_prompt(request: PromptRequest):
    """Process a single prompt using Claude 3.5 with system prompt and word limit."""
    try:
        claude_api_url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": claude_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "claude-3.5",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},  # System instruction
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": WORD_LIMIT_TOKENS
        }
        response = requests.post(claude_api_url, json=payload, headers=headers)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(status_code=500, detail=response_data["error"]["message"])

        return {"prompt": request.prompt, "response": response_data["content"]}
    except Exception as e:
        logging.error(f"Error calling Claude API: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating response from Claude")

# ✅ 3️⃣ CSV Upload for OpenAI Processing
@app.post("/upload-openai")
async def process_openai_csv(file: UploadFile = File(...)):
    """Process a CSV file of prompts using OpenAI and return the output CSV."""
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        df = pd.read_csv(file.file)
        if "prompt" not in df.columns:
            raise HTTPException(status_code=400, detail="Missing 'prompt' column in the CSV file.")
    except Exception:
        raise HTTPException(status_code=400, detail="Error reading the CSV file.")

    responses = []
    for prompt in df["prompt"]:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},  # System instruction
                    {"role": "user", "content": prompt}
                ],
                max_tokens=WORD_LIMIT_TOKENS
            )
            generated_text = response["choices"][0]["message"]["content"]
        except Exception as e:
            generated_text = f"Error generating response: {str(e)}"
        responses.append({"prompt": prompt, "response": generated_text})

    output_file = "processed_openai.csv"
    output_df = pd.DataFrame(responses)
    output_df.to_csv(output_file, index=False)

    return FileResponse(output_file, media_type="text/csv", filename="processed_openai.csv")

# ✅ 4️⃣ CSV Upload for Claude Processing
@app.post("/upload-claude")
async def process_claude_csv(file: UploadFile = File(...)):
    """Process a CSV file of prompts using Claude 3.5 and return the output CSV."""
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        df = pd.read_csv(file.file)
        if "prompt" not in df.columns:
            raise HTTPException(status_code=400, detail="Missing 'prompt' column in the CSV file.")
    except Exception:
        raise HTTPException(status_code=400, detail="Error reading the CSV file.")

    responses = []
    for prompt in df["prompt"]:
        try:
            claude_api_url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": claude_api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "claude-3.5",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},  # System instruction
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": WORD_LIMIT_TOKENS
            }
            response = requests.post(claude_api_url, json=payload, headers=headers)
            response_data = response.json()
            
            if "error" in response_data:
                generated_text = f"Error generating response: {response_data['error']['message']}"
            else:
                generated_text = response_data["content"]
        except Exception as e:
            generated_text = f"Error generating response: {str(e)}"
        responses.append({"prompt": prompt, "response": generated_text})

    output_file = "processed_claude.csv"
    output_df = pd.DataFrame(responses)
    output_df.to_csv(output_file, index=False)

    return FileResponse(output_file, media_type="text/csv", filename="processed_claude.csv")
