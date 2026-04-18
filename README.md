# AI Assistant (Offline AI Clone)

##  Features
- Multi-chat system
- Auto chat naming
- File upload (PDF, TXT, PPTX)
- AI-based question answering
- Chat history storage
- Delete chat feature

##  Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Flask (Python)
- AI Model: LLaMA3 via Ollama
- Database: PostgreSQL

##  How to Run

1. Install dependencies:
pip install flask psycopg2 ollama PyPDF2 python-pptx python-dotenv

2. Start Ollama:
ollama run llama3

3. Run Flask:
python app.py

4. Open browser:


##  Notes
- Runs locally (no internet required after model download)
- Uses environment variables for DB security