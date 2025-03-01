
import whisper
from gtts import gTTS
import base64
import json
import tempfile
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from .lama_logic import extract_text_from_pdf, generate_question, evaluate_answer


class AudioInterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.prev_questions = []
        self.total_marks = 0
        self.section_marks = {"Correct": 10, "Incomplete": 5, "Incorrect": 0}
        self.question_count = 0
        self.resume_text = None
        self.jd_text = None
        self.model = whisper.load_model("base")  # Load Whisper model

        await self.send(json.dumps({"message": "Please upload your resume and job description."}))

    async def disconnect(self, close_code):
        print("Interview ended!")
        await self.send(json.dumps({"message": "Interview ended!"}))

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)

            # Handle Resume Upload
            if "resume" in data:
                resume_path = await self.save_pdf_from_base64(data["resume"], "resume.pdf")
                self.resume_text = extract_text_from_pdf(resume_path)
                print("Resume received and processed.")

            # Handle JD Upload
            elif "job_description" in data:
                jd_path = await self.save_pdf_from_base64(data["job_description"], "job_description.pdf")
                self.jd_text = extract_text_from_pdf(jd_path)
                print("Job description received and processed.")

            # Start Interview if both files are received
            if self.resume_text and self.jd_text:
                print("Interview started! Best of Luck!")
                await self.send(json.dumps({"message": "Interview started! Best of Luck!"}))
                await self.ask_next_question()

            # Handle text answers
            elif "answer" in data:
                print(f"Received text answer: {data['answer']}")
                await self.process_answer(data["answer"])

        # Handle Audio Answer
        if bytes_data:
            await self.process_audio(bytes_data)

    async def process_audio(self, bytes_data):
        print("Audio file received, transcribing...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(bytes_data)
            tmp_file_path = tmp_file.name

        result = self.model.transcribe(whisper.load_audio(tmp_file_path))
        transcription_text = result["text"]

        os.remove(tmp_file_path)  # Cleanup
        print(f"Transcription: {transcription_text}")
        await self.process_answer(transcription_text)

    async def process_answer(self, answer):
        if not self.prev_questions:
            return

        question = self.prev_questions[-1]
        evaluation_result = evaluate_answer(question, answer)

        marks = self.section_marks.get(
            "Correct" if "Correct" in evaluation_result else
            "Incomplete" if "Incomplete" in evaluation_result else
            "Incorrect", 0
        )
        self.total_marks += marks

        await self.send(json.dumps({"evaluation": evaluation_result, "marks": marks}))

        if self.question_count < 5:
            await self.ask_next_question()
        else:
            percentage = (self.total_marks / (5 * 10)) * 100
            await self.send(json.dumps({
                "message": "Interview Complete!",
                "total_marks": self.total_marks,
                "percentage": f"{percentage:.2f}%"
            }))
            await self.close()

    async def ask_next_question(self):
        question = generate_question(self.resume_text, self.jd_text, self.prev_questions)
        if "Error" in question:
            await self.send(json.dumps({"error": "Failed to generate question"}))
            await self.close()
        else:
            self.question_count += 1
            self.prev_questions.append(question)
            print(f"{self.prev_questions[-1]}")

            # Convert question to speech
            tts = gTTS(text=question, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as audio_file:
                tts.save(audio_file.name)
                audio_path = audio_file.name

            # Encode audio as Base64
            with open(audio_path, "rb") as f:
                audio_base64 = base64.b64encode(f.read()).decode("utf-8")

            os.remove(audio_path)  # Cleanup

            await self.send(json.dumps({
                "question": question,
                "audio": audio_base64
            }))

    async def save_pdf_from_base64(self, base64_string, filename):
        """Decode base64 string and save it as a PDF file."""
        file_data = base64.b64decode(base64_string)
        file_path = os.path.join(tempfile.gettempdir(), filename)
        with open(file_path, "wb") as f:
            f.write(file_data)
        return file_path

