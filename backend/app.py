from flask import Flask, request, render_template
from PyPDF2 import PdfReader
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def clean_text(text):
    text = text.replace("\x7f", "")
    text = text.replace("\n\n", "\n")
    return text.strip()


def extract_skills(text):
    skills = []

    lines = text.splitlines()

    for i, line in enumerate(lines):
        if line.strip().upper() == "SKILLS":
            for next_line in lines[i + 1:]:
                if next_line.strip().upper() in [
                    "PROJECTS",
                    "CERTIFICATIONS",
                    "HOBBIES",
                    "LANGUAGES KNOWN",
                    "CAREER INTEREST",
                    "DECLARATION"
                ]:
                    break

                if next_line.strip():
                    skills.append(next_line.strip())

            break

    return skills


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_resume():
    resume = request.files["resume"]

    if resume:
        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume.filename
        )

        resume.save(file_path)

        reader = PdfReader(file_path)
        text = ""

        for page in reader.pages:
            extracted_text = page.extract_text()

            if extracted_text:
                text += extracted_text

        text = clean_text(text)

        skills = extract_skills(text)

        return str(skills)

    return "No resume selected."


if __name__ == "__main__":
    app.run(debug=True)