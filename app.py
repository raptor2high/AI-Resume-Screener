import streamlit as st
import pandas as pd
from utils import (
    extract_text_from_pdf,
    extract_text_from_txt,
    clean_text,
    extract_keywords,
    calculate_match_score,
    find_missing_skills,
    generate_suggestions
)

# Page configuration
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for attractive UI
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
    }
    .score-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .score-low { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .score-medium { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
    .score-high { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
    .highlight {
        background-color: #fff4e6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("# 📄 AI Resume Screener")
st.markdown("### Match your resume with job descriptions using AI-powered analysis")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("## 📊 About This Tool")
    st.info("""
    This app uses **TF-IDF vectorization** and **cosine similarity** to:
    
    - 🎯 Calculate match percentage
    - 🔍 Identify missing skills
    - 💡 Provide improvement suggestions
    - 📈 Extract key keywords
    
    **Supported formats:** PDF, TXT
    """)

# Main layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📤 Upload Resume")
    resume_file = st.file_uploader("Upload your resume", type=['pdf', 'txt'])
    resume_text = ""
    
    if resume_file:
        if resume_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(resume_file)
        else:
            resume_text = extract_text_from_txt(resume_file)
        
        if "Error" not in resume_text:
            st.success(f"✅ Resume uploaded ({len(resume_text)} characters)")
        else:
            st.error(resume_text)

with col2:
    st.markdown("## 📝 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Paste the complete job description..."
    )

st.divider()

# Analysis section
if resume_text and job_description and "Error" not in resume_text:
    if st.button("🚀 Analyze Match", use_container_width=True, type="primary"):
        with st.spinner("🔍 Analyzing..."):
            # Calculate match score
            match_score, cleaned_resume, cleaned_job = calculate_match_score(
                resume_text, job_description
            )
            
            # Find missing skills
            missing_skills, present_skills = find_missing_skills(
                cleaned_resume, cleaned_job
            )
            
            # Generate suggestions
            job_keywords = extract_keywords(cleaned_job)
            suggestions = generate_suggestions(match_score, missing_skills, job_keywords)
            
            # Display results
            st.markdown("## 📊 Analysis Results")
            
            # Match Score
            score_class = "score-low" if match_score < 30 else "score-medium" if match_score < 60 else "score-high"
            st.markdown(
                f'<div class="score-container {score_class}">Match: {match_score}%</div>',
                unsafe_allow_html=True
            )
            
            # Results tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🎯 Overview", "🔍 Skills Analysis", "📈 Keywords", "💡 Suggestions"])
            
            with tab1:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Match Score", f"{match_score}%")
                with col2:
                    st.metric("Matching Skills", len(present_skills))
                with col3:
                    st.metric("Missing Skills", len(missing_skills))
            
            with tab2:
                st.markdown("### ✅ Skills Present in Both")
                if present_skills:
                    skills_df = pd.DataFrame({
                        "Skill": present_skills[:20]
                    })
                    st.dataframe(skills_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No overlapping skills found. Review the job requirements.")
                
                st.markdown("### ❌ Missing Skills")
                if missing_skills:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        missing_df = pd.DataFrame({
                            "Missing Skill": missing_skills[:20],
                            "Importance": ["High"] * 5 + ["Medium"] * (len(missing_skills) - 5) if len(missing_skills) > 5 else ["High"] * len(missing_skills)
                        })
                        st.dataframe(missing_df, use_container_width=True, hide_index=True)
                else:
                    st.success("No missing skills detected! 🎉")
            
            with tab3:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📌 Top Resume Keywords")
                    resume_keywords = extract_keywords(cleaned_resume, top_n=10)
                    resume_kw_df = pd.DataFrame({
                        "Keyword": resume_keywords.keys(),
                        "Frequency": resume_keywords.values()
                    })
                    st.bar_chart(resume_kw_df.set_index("Keyword"))
                
                with col2:
                    st.markdown("### 📌 Top Job Keywords")
                    job_kw_df = pd.DataFrame({
                        "Keyword": job_keywords.keys(),
                        "Frequency": job_keywords.values()
                    })
                    st.bar_chart(job_kw_df.set_index("Keyword"))
            
            with tab4:
                st.markdown("### 💡 Improvement Suggestions")
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"**{i}. {suggestion}**")
                
                st.markdown("---")
                st.markdown("### 🎯 Action Items")
                with st.expander("📋 Download Analysis Report"):
                    report = f"""
# Resume Screening Analysis Report

## Match Score: {match_score}%

## Summary
- Total Matching Skills: {len(present_skills)}
- Missing Skills: {len(missing_skills)}

## Matching Keywords
{', '.join(present_skills[:15])}

## Missing Keywords
{', '.join(missing_skills[:15])}

## Recommendations
{chr(10).join([f"- {s}" for s in suggestions])}
                    """
                    st.download_button(
                        label="📥 Download Report (Text)",
                        data=report,
                        file_name="resume_analysis.txt",
                        mime="text/plain"
                    )
else:
    st.warning("⚠️ Please upload a resume and provide a job description to begin analysis.")

st.divider()
st.markdown("""
<div style='text-align: center; color: #888; margin-top: 3rem;'>
    <p>Made with ❤️ using Streamlit | AI Resume Screener v1.0</p>
    <p style='font-size: 0.9rem;'>This tool helps identify skill gaps using TF-IDF based similarity analysis</p>
</div>
""", unsafe_allow_html=True)
