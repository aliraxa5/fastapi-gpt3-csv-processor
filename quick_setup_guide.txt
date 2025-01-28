# FastAPI Project Setup (Quick Guide)

## 1️⃣ Install Python (3.9 or newer)
Download: https://www.python.org/downloads/

## 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate   # Git Bash (Windows)
venv\Scripts\activate        # Command Prompt (Windows)
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 4️⃣ Set OpenAI API Key
- Get API Key: https://platform.openai.com/api-keys
- Create a `.env` file and add:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```

## 5️⃣ Run the FastAPI Server
```bash
uvicorn main:app --reload
```

## 6️⃣ Test API in Browser
- Open: http://127.0.0.1:8000/docs
- Upload a CSV to `/process-prompts` and download results.
