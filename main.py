import os
import pandas as pd
import openai
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Configure logging for better debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}

@app.post("/process-prompts")
async def process_prompts(file: UploadFile = File(...)):
    """Process uploaded CSV file, generate AI responses, and return the output CSV."""

    # ✅ Step 1: Validate that the uploaded file is a CSV
    if file.content_type != "text/csv":
        logging.error("Invalid file format. Must be a CSV.")
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        # ✅ Step 2: Read CSV
        df = pd.read_csv(file.file)
    except Exception:
        logging.error("Error reading the CSV file.")
        raise HTTPException(status_code=400, detail="Error reading the CSV file.")

    # ✅ Step 3: Ensure 'prompt' column exists
    if 'prompt' not in df.columns:
        logging.error("Missing 'prompt' column in CSV file.")
        raise HTTPException(status_code=400, detail="Missing 'prompt' column in the CSV file.")

    # ✅ Step 4: Process prompts using OpenAI
    responses = []
    for prompt in df['prompt']:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            generated_text = response['choices'][0]['message']['content']
            logging.info(f"Generated response for: {prompt}")
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {str(e)}")
            generated_text = f"Error generating response: {str(e)}"

        responses.append({"prompt": prompt, "response": generated_text})

    # ✅ Step 5: Save results to a new CSV file
    output_file = "processed_prompts.csv"
    output_df = pd.DataFrame(responses)
    output_df.to_csv(output_file, index=False)

    # ✅ Step 6: Return the processed CSV file as a downloadable response
    return FileResponse(output_file, media_type="text/csv", filename="processed_prompts.csv")
