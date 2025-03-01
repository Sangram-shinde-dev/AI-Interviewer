# AI-Interviewer

AI-Interviewer is an AI-powered interview platform that conducts technical interviews dynamically based on the candidate's resume and job description. It evaluates responses in real-time and generates performance reports.

## Features
- AI-driven question generation based on the resume and job description.
- Audio and text answer support with real-time transcription using Whisper.
- AI-based answer evaluation and scoring.

## Tech Stack
- **Backend:** Django Rest Framework (DRF), Django Channels, WebSockets
- **AI Processing:** Whisper (speech-to-text), GPT-based LLM (for question generation and evaluation)

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.11+
- Django & Django Channels
- Whisper, gTTS, pdfplumber


### Setup
Clone the repository:
```sh
git clone https://github.com/yourusername/AI-Interviewer.git
cd AI-Interviewer
```

Create a virtual environment and install dependencies:
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

Set up environment variables:
Create a `.env` file in the root directory and add:
```
SECRET_KEY=your_django_secret_key
OLLAMA_SERVER_URL=your_ai_model_server_url
DEBUG=True  # Change to False in production
```

Run database migrations:
```sh
python manage.py migrate
```

Start the development server:
```sh
python manage.py runserver
```

Start WebSocket server (if applicable):
```sh
python manage.py runworker
```

## Usage
### Starting an Interview
1. The AI generates and asks interview questions dynamically.
2. The candidate answers via text or audio.
3. The AI evaluates and scores responses.
4. A final report is generated at the end of the interview.


