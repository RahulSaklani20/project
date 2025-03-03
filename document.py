import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Helper function to read file content
def read_file(file_path):
    print(file_path, "path")
    with open(file_path, 'rb') as f:  # Open in binary mode
        raw_data = f.read()
    
    # Try decoding with UTF-8 first
    try:
        content = raw_data.decode('utf-8')
    except UnicodeDecodeError:
        # Fallback to latin-1 if UTF-8 fails
        content = raw_data.decode('latin-1')
    
    print(content, "skfhaoishfdi")
    return content

# Helper function to calculate Levenshtein similarity
def levenshtein_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

# Helper function to calculate cosine similarity
def cosine_similarity_score(text1, text2):
    print(text1, text2, "text1, text2")
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

# Upload document to the database
def upload_document(user_id, file_path):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO documents (user_id, file_path, upload_date) VALUES (?, ?, ?)',
              (user_id, file_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Get matching documents
def get_matching_documents(doc_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Get the current document's file path and content
    c.execute('SELECT file_path FROM documents WHERE id = ?', (doc_id,))
    current_doc_path = c.fetchone()[0]
    current_doc_text = read_file(current_doc_path)

    # Get all other documents
    c.execute('SELECT id, file_path FROM documents WHERE id != ?', (doc_id,))
    all_docs = c.fetchall()

    matching_docs = []
    for doc in all_docs:
        doc_id_other, doc_path_other = doc
        doc_text_other = read_file(doc_path_other)

        # Calculate similarity scores
        levenshtein_score = levenshtein_similarity(current_doc_text, doc_text_other)
        cosine_score = cosine_similarity_score(current_doc_text, doc_text_other)

        # Average the scores (you can adjust weights as needed)
        combined_score = (levenshtein_score + cosine_score) / 2

        # Add to matching documents if similarity is above a threshold
        if combined_score > 0.7:  # Adjust threshold as needed
            matching_docs.append({
                'id': doc_id_other,
                'levenshtein_similarity': levenshtein_score,
                'cosine_similarity': cosine_score,
                'combined_score': combined_score
            })

    conn.close()
    return matching_docs