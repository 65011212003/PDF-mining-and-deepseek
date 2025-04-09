import PyPDF2
import sqlite3
import os
from datetime import datetime

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def init_db():
    """Initialize SQLite database and create table."""
    conn = sqlite3.connect('pdf_extracts.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_data
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      filename TEXT,
                      content TEXT,
                      processed_at TIMESTAMP)''')
    conn.commit()
    return conn

def save_to_db(conn, filename, content):
    """Save extracted text to database."""
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO pdf_data (filename, content, processed_at)
                      VALUES (?, ?, ?)''', 
                   (filename, content, datetime.now()))
    conn.commit()

if __name__ == "__main__":
    conn = init_db()
    pdf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'papers')
    
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            extracted_text = extract_text_from_pdf(pdf_path)
            if extracted_text:
                save_to_db(conn, filename, extracted_text)
                print(f"Successfully processed {filename}")
            else:
                print(f"Failed to extract text from {filename}")
    
    conn.close()