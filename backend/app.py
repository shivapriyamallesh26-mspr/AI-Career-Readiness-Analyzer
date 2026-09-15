from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AI Career Readiness Analyzer is running!"

if __name__ == "__main__":
    app.run(debug=True)
    