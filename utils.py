import re
import PyPDF2
from io import BytesIO
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_text_from_txt(txt_file):
    """Extract text from uploaded TXT file."""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        return f"Error reading TXT: {str(e)}"


def clean_text(text):
    """Clean and normalize text."""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and extra whitespace
    text = re.sub(r'[^a-z0-9\s+#]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_keywords(text, top_n=15):
    """Extract top keywords from text."""
    # Split and count word frequencies
    words = text.split()
    # Filter common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
        'may', 'might', 'must', 'can', 'as', 'if', 'than', 'that', 'this',
        'which', 'who', 'where', 'when', 'why', 'how', 'all', 'each', 'every',
        'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor'
    }
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    word_freq = pd.Series(filtered_words).value_counts().head(top_n)
    return word_freq.to_dict()


def calculate_match_score(resume_text, job_description):
    """Calculate match score between resume and job description using TF-IDF and cosine similarity."""
    # Clean texts
    resume_cleaned = clean_text(resume_text)
    job_cleaned = clean_text(job_description)
    
    # Vectorize
    vectorizer = TfidfVectorizer(max_features=100, analyzer='word')
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_cleaned, job_cleaned])
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        match_score = round(similarity * 100, 2)
    except:
        match_score = 0
    
    return match_score, resume_cleaned, job_cleaned


def find_missing_skills(resume_text, job_description):
    """Identify skills present in job description but missing in resume."""
    resume_keywords = set(extract_keywords(resume_text).keys())
    job_keywords = set(extract_keywords(job_description).keys())
    
    missing = job_keywords - resume_keywords
    present = resume_keywords & job_keywords
    
    return list(missing), list(present)


def generate_suggestions(match_score, missing_skills, job_keywords):
    """Generate actionable suggestions based on analysis."""
    suggestions = []
    
    if match_score < 30:
        suggestions.append("⚠️ Low match score. Consider reviewing the job requirements and updating your resume with relevant skills.")
    elif match_score < 60:
        suggestions.append("📝 Moderate match. Look to highlight more relevant experience and skills from the job description.")
    else:
        suggestions.append("✅ Good match! Ensure you emphasize these matching skills in your interview.")
    
    if missing_skills:
        suggestions.append(f"🎯 Add these {len(missing_skills)} missing keywords to improve your match: {', '.join(missing_skills[:5])}")
    else:
        suggestions.append("🌟 Your resume aligns well with most job requirements!")
    
    suggestions.append("💡 Tip: Use the exact terminology from the job description in your resume to improve ATS compatibility.")
    
    return suggestions
