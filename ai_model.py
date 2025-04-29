import os
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import random
from datetime import datetime

# Load the dataset
df = pd.read_csv('fir_sections.csv')

# Initialize the TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df['Description'])

# Configure the Groq client
client = Groq(api_key="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")

def get_relevant_sections(case_description):
    """Find relevant IPC sections based on case description using TF-IDF and cosine similarity"""
    case_vector = vectorizer.transform([case_description])
    cosine_similarities = cosine_similarity(case_vector, tfidf_matrix).flatten()
    
    # Get top 5 most similar sections
    top_indices = cosine_similarities.argsort()[-5:][::-1]
    
    relevant_sections = {}
    for index in top_indices:
        if cosine_similarities[index] > 0.1:  # Only include if similarity is above threshold
            relevant_sections[df.iloc[index]['Section']] = df.iloc[index]['Description']
    
    return relevant_sections

def get_sections_and_analysis(case_description):
    """Get relevant sections and analysis for the case description"""
    relevant_sections = get_relevant_sections(case_description)
    
    sections_prompt = f"""
    You are a legal expert specializing in Indian criminal law. Based on the following case description, provide a comprehensive list of all possible relevant sections from the Indian Penal Code (IPC) and other applicable acts.

    Case Description: {case_description}

    Initial Relevant Sections from Analysis:
    {relevant_sections}

    Please provide:
    1. A complete list of applicable sections with brief explanations of why each section applies
    2. Any additional sections that might be relevant but weren't in the initial analysis
    3. A detailed legal analysis of the case considering:
       - Primary offenses
       - Secondary or related offenses
       - Aggravating factors
       - Procedural considerations
       - Potential defenses

    Format your response as:
    APPLICABLE SECTIONS:
    Section [Number] - [Brief explanation of relevance]
    
    CASE ANALYSIS:
    [Detailed analysis of the legal aspects of the case]
    
    INVESTIGATION RECOMMENDATIONS:
    [Suggestions for evidence collection and next steps]
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a legal assistant specializing in Indian criminal law."},
                {"role": "user", "content": sections_prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return relevant_sections, completion.choices[0].message.content
    except Exception as e:
        # Fallback in case of API error
        print(f"Error calling Groq API: {e}")
        return relevant_sections, "API error occurred. Please try again later."

def generate_fir_structure(case_description, relevant_sections, user_inputs):
    """Generate a structured FIR based on case description and user inputs"""
    # Generate a random FIR number
    current_year = datetime.now().year
    fir_number = f"{random.randint(1, 999)}/{current_year}"
    
    prompt = f"""
    You are a senior police officer with expertise in drafting First Information Reports (FIRs) in India. 
    Based on the following information, generate a professionally formatted FIR document.

    CASE DESCRIPTION:
    {case_description}

    RELEVANT SECTIONS:
    {relevant_sections}

    USER INPUTS:
    {user_inputs}

    FIR NUMBER: {fir_number}
    REGISTRATION DATE: {datetime.now().strftime('%d-%m-%Y')}

    Please format the FIR with the following sections:
    
    FIRST INFORMATION REPORT
    
    1. FIR Number and Registration Details
    2. Date, Time and Place of Occurrence
    3. Information Received At Police Station (use current date/time)
    4. Type of Information: Written/Oral
    5. Complainant Details (name, address, contact)
    6. Details of Known/Unknown Accused
    7. Reasons for delay in reporting (if applicable)
    8. Particulars of properties stolen (if applicable)
    9. Description of the Incident (detailed facts)
    10. Sections of Law Applied
    11. Action Taken (initial steps)
    12. Signature/Thumb Impression of Complainant
    13. Officer Details (use "Investigating Officer, [Police Station Name]")

    Format the FIR in a clear, professional manner suitable for official police records. Use formal language appropriate for legal documents.
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a legal assistant specializing in Indian criminal law."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return completion.choices[0].message.content
    except Exception as e:
        # Fallback in case of API error
        print(f"Error calling Groq API: {e}")
        return "API error occurred. Please try again later."