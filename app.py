from flask import Flask, render_template, request, jsonify
import ollama
import PyPDF2
import psycopg2
from pptx import Presentation
from dotenv import load_dotenv
import os

app = Flask(__name__)

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- DATABASE CONNECTION ----------------
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

# ---------------- GLOBAL VARIABLES ----------------
file_text = ""
current_chat_id = None

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- CHAT ----------------
@app.route("/chat", methods=["POST"])
def chat():
    global current_chat_id, file_text

    try:
        user_input = request.json.get("message")

        #Create chat if not exists
        if current_chat_id is None:
            cur.execute(
                "INSERT INTO chats (title) VALUES (%s) RETURNING id",
                ("New Chat",)
            )
            current_chat_id = cur.fetchone()[0]
            conn.commit()

        # Limit file text
        context = file_text[:2000] if file_text else ""

        # Create prompt
        if context:
            prompt = f"""
            Answer based on this content:

            {context}

            Question: {user_input}
            """
        else:
            prompt = user_input

        # AI response
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_reply = response["message"]["content"]

        # UPDATE TITLE AFTER FIRST MESSAGE
        cur.execute("SELECT title FROM chats WHERE id=%s", (current_chat_id,))
        current_title = cur.fetchone()[0]

        if current_title == "New Chat":
            new_title = user_input[:25] + "..." if len(user_input) > 25 else user_input

            cur.execute(
                "UPDATE chats SET title=%s WHERE id=%s",
                (new_title, current_chat_id)
            )
            conn.commit()

        # Save message
        save_chat(current_chat_id, user_input, ai_reply)

        return jsonify({"response": ai_reply})

    except Exception as e:
        print("CHAT ERROR:", e)
        conn.rollback()
        return jsonify({"response": "Error occurred"})
# ---------------- SAVE CHAT ----------------
def save_chat(chat_id, user_msg, ai_msg):
    try:
        cur.execute(
            "INSERT INTO messages (chat_id, user_msg, ai_msg) VALUES (%s, %s, %s)",
            (chat_id, user_msg, ai_msg)
        )
        conn.commit()
    except Exception as e:
        print("DB ERROR:", e)
        conn.rollback()

# ---------------- FILE UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    global file_text

    try:
        file = request.files["file"]
        filename = file.filename.lower()

        file_text = ""

        # -------- PDF --------
        if filename.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                file_text += page.extract_text() or ""

        # -------- TXT --------
        elif filename.endswith(".txt"):
            file_text = file.read().decode("utf-8")

        # -------- PPTX --------
        elif filename.endswith(".pptx"):
            prs = Presentation(file)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        file_text += shape.text + "\n"

        else:
            return jsonify({"response": "Unsupported file type ❌"})

        if not file_text.strip():
            return jsonify({"response": "No readable text found ❌"})

        return jsonify({"response": "File processed successfully ✅"})

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"response": "Upload failed ❌"})

# ---------------- GET ALL CHATS ----------------
@app.route("/get_chats")
def get_chats():
    try:
        cur.execute("SELECT id, title FROM chats ORDER BY id DESC")
        chats = cur.fetchall()

        return jsonify([{"id": c[0], "title": c[1]} for c in chats])

    except Exception as e:
        print("GET CHATS ERROR:", e)
        conn.rollback()
        return jsonify([])

# ---------------- GET MESSAGES OF CHAT ----------------
@app.route("/get_messages/<int:chat_id>")
def get_messages(chat_id):
    try:
        global current_chat_id
        current_chat_id = chat_id

        cur.execute(
            "SELECT user_msg, ai_msg FROM messages WHERE chat_id=%s ORDER BY id",
            (chat_id,)
        )
        rows = cur.fetchall()

        return jsonify([{"user": r[0], "bot": r[1]} for r in rows])

    except Exception as e:
        print("GET MESSAGES ERROR:", e)
        conn.rollback()
        return jsonify([])

# ---------------- NEW CHAT ----------------
@app.route("/new_chat", methods=["POST"])
def new_chat():
    global current_chat_id, file_text

    try:
        cur.execute(
            "INSERT INTO chats (title) VALUES (%s) RETURNING id",
            ("New Chat",)
        )
        current_chat_id = cur.fetchone()[0]
        conn.commit()

        file_text = ""  # reset file context

        return jsonify({"chat_id": current_chat_id})

    except Exception as e:
        print("NEW CHAT ERROR:", e)
        conn.rollback()
        return jsonify({"error": "failed"})
    
@app.route("/delete_chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    try:
        # delete messages first (important)
        cur.execute("DELETE FROM messages WHERE chat_id=%s", (chat_id,))
        
        # delete chat
        cur.execute("DELETE FROM chats WHERE id=%s", (chat_id,))
        
        conn.commit()

        return jsonify({"status": "deleted"})

    except Exception as e:
        print("DELETE ERROR:", e)
        conn.rollback()
        return jsonify({"error": "failed"})
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)