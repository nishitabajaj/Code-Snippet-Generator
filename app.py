import sqlite3
from flask import Flask, request, render_template_string
import openai
from datetime import datetime

# Set your OpenAI API key
openai.api_key = "secret key"
app = Flask(__name__)

# Database name
DB_NAME = "code_snippet.db"

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS code_snippet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            snippet TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# Generate code snippet using ChatGPT API
def generate_code_snippet(task):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model
            messages=[
                {"role": "system", "content": "You are a programming assistant. Generate code snippets for the given tasks."},
                {"role": "user", "content": task}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Log task and generated code snippet to the database
def log_to_db(task, snippet):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO code_snippet (task, snippet, timestamp) VALUES (?, ?, ?)", (task, snippet, timestamp))
    conn.commit()
    conn.close()

# Web interface
@app.route("/", methods=["GET", "POST"])
def index():
    snippet = ""
    if request.method == "POST":
        task = request.form["task"]
        snippet = generate_code_snippet(task)
        log_to_db(task, snippet)
    
    # HTML template
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Code Snippet Generator(Nishita Bajaj)</title>
    </head>
    <body>
        <h1>Code Snippet Generator</h1>
        <form method="POST">
            <label for="task">Enter question to generate code snippet for:</label><br>
            <input type="text" id="task" name="task" required><br><br>
            <button type="submit">Generate Code</button>
        </form>
        {% if snippet %}
        <h3>Generated Code Snippet:</h3>
        <pre>{{ snippet }}</pre>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html_template, snippet=snippet)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)