
OLLAMA_SERVER_URL = "Your Ollma Server UrL"

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def generate_question(resume_text, jd_text, prev_questions, server_url=OLLAMA_SERVER_URL):
    """Generate a new question based on resume and job description."""
    prompt = f"""
    You are an AI-powered interview assistant helping HR professionals assess candidates.

    ### **Candidate’s Resume:**
    {resume_text}

    ### **Job Description:**
    {jd_text}

    ### **Previously Asked Questions (Do NOT repeat these):**
    {prev_questions if prev_questions else "None"}

    👉 **Generate ONE new question.**
    """

    try:
        response = requests.post(
            f"{server_url}/api/generate",
            json={"model": "mistral", "prompt": prompt, "stream": False},
        )
        if response.status_code == 200:
            return response.json().get("response", "Error: Empty response").strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def evaluate_answer(question, answer, server_url=OLLAMA_SERVER_URL):
    """Evaluate the candidate's answer to a given question."""
    evaluation_prompt = f"""
    You are an AI interview evaluator.

    ### **Question:**  
    {question}

    ### **Candidate’s Answer:**  
    {answer}

    👉 **Evaluate the response.**
    """

    try:
        response = requests.post(
            f"{server_url}/api/generate",
            json={"model": "mistral", "prompt": evaluation_prompt, "stream": False},
        )
        if response.status_code == 200:
            return response.json().get("response", "Error: Empty response").strip()
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
