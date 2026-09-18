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

        return text

    return "No resume selected."


if __name__ == "__main__":
    app.run(debug=True)