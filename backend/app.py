from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
import os
import re

app = Flask(__name__)
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# KNOWN SKILLS
# --------------------------------------------------

KNOWN_SKILLS = [
    "C Programming",
    "C++",
    "Java",
    "Python",
    "JavaScript",
    "HTML",
    "CSS",
    "SQL",
    "MongoDB",
    "MySQL",
    "Git",
    "GitHub",
    "Flask",
    "Communication",
    "Teamwork",
    "Problem Solving",
    "MS Excel",
    "MS Word",
    "Typing Skills",
    "Quick Learning",
    "PDF Processing",
    "OpenAI API",
    "AI",
    "Machine Learning",
    "Data Analysis"
]


# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_pdf_text(path):

    text = ""

    try:

        reader = PdfReader(path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    except Exception as e:

        print("PDF extraction error:", e)

    return text


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):

    if not text:
        return ""

    text = text.replace("\x7f", "")

    text = re.sub(
        r"\n\s*\n+",
        "\n",
        text
    )

    return text.strip()


# --------------------------------------------------
# SKILL EXTRACTION
# --------------------------------------------------

def extract_skills(text):

    text_lower = text.lower()

    return [
        skill
        for skill in KNOWN_SKILLS
        if skill.lower() in text_lower
    ]


# --------------------------------------------------
# EDUCATION EXTRACTION
# --------------------------------------------------

def extract_education(text):

    keywords = [
        "b.tech",
        "btech",
        "b.e",
        "bachelor",
        "computer science",
        "information technology",
        "engineering",
        "m.tech",
        "mca",
        "degree",
        "intermediate",
        "12th",
        "10th",
        "ssc"
    ]

    education = []

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        if any(
            keyword in line.lower()
            for keyword in keywords
        ):

            education.append(line)

    return education


# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------

def extract_projects(text):

    projects = []

    active = False

    stop_words = [
        "education",
        "certification",
        "experience",
        "skills",
        "achievement",
        "internship",
        "coursework"
    ]

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if "project" in lower:

            active = True

            continue

        if active:

            if any(
                word in lower
                for word in stop_words
            ):

                active = False

            elif len(line) > 5:

                projects.append(line)

    return projects[:10]


# --------------------------------------------------
# CERTIFICATION EXTRACTION
# --------------------------------------------------

def extract_certifications(text):

    certifications = []

    active = False

    stop_words = [
        "education",
        "project",
        "experience",
        "skills",
        "achievement",
        "internship"
    ]

    for line in text.split("\n"):

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if (
            "certification" in lower
            or "certificate" in lower
        ):

            active = True

            continue

        if active:

            if any(
                word in lower
                for word in stop_words
            ):

                active = False

            elif len(line) > 5:

                certifications.append(line)

    return certifications[:10]


# --------------------------------------------------
# JOB SKILL EXTRACTION
# --------------------------------------------------

def extract_job_skills(job):

    lower = job.lower()

    return [
        skill
        for skill in KNOWN_SKILLS
        if skill.lower() in lower
    ]


# --------------------------------------------------
# JOB MATCH
# --------------------------------------------------

def calculate_job_match(
    resume,
    job
):

    if not job:
        return 0

    matching = [
        skill
        for skill in job
        if skill in resume
    ]

    return round(
        len(matching) / len(job) * 100
    )


# --------------------------------------------------
# SKILL GAPS
# --------------------------------------------------

def generate_skill_gaps(
    resume,
    job
):

    return [
        skill
        for skill in job
        if skill not in resume
    ]


# --------------------------------------------------
# RESUME SCORE
# --------------------------------------------------

def calculate_resume_score(
    resume,
    job,
    education,
    projects,
    certifications
):

    if job:

        technical = calculate_job_match(
            resume,
            job
        )

    else:

        technical = 100 if resume else 0

    job_match = calculate_job_match(
        resume,
        job
    )

    project_score = 100 if projects else 0

    education_score = 100 if education else 0

    certification_score = 100 if certifications else 0

    final_score = (

        technical * 0.40

        + job_match * 0.25

        + project_score * 0.15

        + education_score * 0.10

        + certification_score * 0.10

    )

    return round(final_score)


# --------------------------------------------------
# PRIORITY SKILL GAPS
# --------------------------------------------------

HIGH_PRIORITY = {
    "Python",
    "HTML",
    "CSS",
    "Git",
    "GitHub",
    "Flask"
}


MEDIUM_PRIORITY = {
    "PDF Processing",
    "OpenAI API",
    "Data Analysis",
    "SQL",
    "Machine Learning"
}


PRIORITY_REASONS = {

    "Python":
        "Python is a core requirement for developing the target applications.",

    "HTML":
        "HTML is needed to build the web interface.",

    "CSS":
        "CSS is needed to create a usable web application interface.",

    "Git":
        "Git is important for version control and collaborative development.",

    "GitHub":
        "GitHub is useful for managing and showcasing development projects.",

    "Flask":
        "Flask is required for Python-based web application development.",

    "PDF Processing":
        "PDF processing is directly related to resume and document analysis.",

    "OpenAI API":
        "OpenAI API knowledge is useful for integrating AI features.",

    "Data Analysis":
        "Data analysis is useful for processing and understanding application data.",

    "SQL":
        "SQL is useful for storing and analyzing structured application data.",

    "Machine Learning":
        "Machine learning concepts can support AI-powered application development."

}


def generate_priority_skill_gaps(missing):

    result = []

    for skill in missing:

        if skill in HIGH_PRIORITY:

            priority = "High"

        elif skill in MEDIUM_PRIORITY:

            priority = "Medium"

        else:

            priority = "Low"

        result.append({

            "skill": skill,

            "priority": priority,

            "reason": PRIORITY_REASONS.get(
                skill,
                f"{skill} is relevant to the target job."
            )

        })

    return result


# --------------------------------------------------
# PERSONALIZED LEARNING ROADMAP
# --------------------------------------------------

ROADMAP = {

    "Python": (
        "High",
        "1–2 weeks",
        "Python is a core requirement for the target role.",
        [
            "Learn variables, data types, operators and conditions.",
            "Practice loops, functions, lists and dictionaries.",
            "Learn file handling and basic error handling."
        ],
        "Build a Student Performance Analyzer using Python.",
        "Build at least one working Python project."
    ),

    "HTML": (
        "High",
        "4–5 days",
        "HTML is required to create the structure of web applications.",
        [
            "Learn headings, paragraphs, links, images and forms.",
            "Practice semantic HTML elements.",
            "Create a structured web page."
        ],
        "Build a personal portfolio webpage.",
        "Create one complete HTML webpage."
    ),

    "CSS": (
        "High",
        "5–7 days",
        "CSS is required to design and style web applications.",
        [
            "Learn selectors, colors, spacing and the box model.",
            "Practice Flexbox and responsive design.",
            "Create mobile-friendly layouts."
        ],
        "Build a responsive career dashboard.",
        "Create a responsive webpage that works on mobile and desktop."
    ),

    "Git": (
        "High",
        "3–4 days",
        "Git is important for version control and software development.",
        [
            "Learn git init, status, add and commit.",
            "Practice branches and merging.",
            "Use Git regularly while developing projects."
        ],
        "Maintain your projects using Git.",
        "Be able to create commits, branches and merge changes."
    ),

    "GitHub": (
        "High",
        "2–3 days",
        "GitHub helps you showcase projects and collaborate with developers.",
        [
            "Learn repositories and README files.",
            "Practice push, pull and cloning.",
            "Create a professional project repository."
        ],
        "Create a professional GitHub portfolio.",
        "Upload your major projects with proper README files."
    ),

    "Flask": (
        "High",
        "5–7 days",
        "Flask is required for Python-based web application development.",
        [
            "Learn Flask application structure.",
            "Practice routes and HTTP methods.",
            "Learn templates, forms and POST requests."
        ],
        "Build a Flask-based Student Management System.",
        "Create a working Flask web application."
    ),

    "PDF Processing": (
        "Medium",
        "3–4 days",
        "PDF processing is directly related to your resume analyzer.",
        [
            "Understand basic PDF file handling.",
            "Learn text extraction using PyPDF2.",
            "Handle PDFs that contain missing or empty text."
        ],
        "Build a PDF Resume Text Extractor.",
        "Extract and display text from uploaded PDF files."
    ),

    "OpenAI API": (
        "Medium",
        "3–5 days",
        "AI APIs are useful for building AI-powered applications.",
        [
            "Understand APIs and request-response flow.",
            "Learn how API keys are used securely.",
            "Practice sending prompts to an AI API."
        ],
        "Build an AI Interview Question Generator.",
        "Create one application that integrates an AI API."
    ),

    "Data Analysis": (
        "Medium",
        "5–7 days",
        "Data analysis helps in understanding and processing structured data.",
        [
            "Learn data cleaning concepts.",
            "Practice working with tables and datasets.",
            "Learn basic analysis and visualization."
        ],
        "Build a Student Performance Analysis project.",
        "Analyze a dataset and present useful insights."
    ),

    "SQL": (
        "Medium",
        "1 week",
        "SQL is useful for storing and retrieving structured application data.",
        [
            "Learn SELECT, INSERT, UPDATE and DELETE.",
            "Practice WHERE, ORDER BY and GROUP BY.",
            "Learn JOIN and basic database design."
        ],
        "Build a College Database Management System.",
        "Create a database project with multiple related tables."
    ),

    "Machine Learning": (
        "Medium",
        "2–3 weeks",
        "Machine learning concepts support AI-powered applications.",
        [
            "Learn supervised and unsupervised learning.",
            "Understand training and testing data.",
            "Learn basic classification and regression."
        ],
        "Build a Student Performance Prediction system.",
        "Train and test one basic machine learning model."
    ),

    "MongoDB": (
        "Low",
        "4–7 days",
        "MongoDB can be useful for storing flexible application data.",
        [
            "Learn databases, collections and documents.",
            "Practice CRUD operations.",
            "Connect MongoDB with a web application."
        ],
        "Build a MongoDB-based Job Application Tracker.",
        "Create an application that stores and retrieves data from MongoDB."
    ),

    "MySQL": (
        "Low",
        "4–7 days",
        "MySQL is useful for relational database applications.",
        [
            "Learn tables, rows and columns.",
            "Practice CRUD operations.",
            "Connect MySQL with a small application."
        ],
        "Build a Student Attendance Management System.",
        "Create a working database-based application."
    ),

    "Java": (
        "Medium",
        "1–2 weeks",
        "Java is useful for object-oriented programming and software development.",
        [
            "Practice classes and objects.",
            "Learn inheritance and polymorphism.",
            "Practice arrays, strings and collections."
        ],
        "Build a Java Student Management System.",
        "Create one complete Java OOP project."
    ),

    "C++": (
        "Medium",
        "1–2 weeks",
        "C++ strengthens programming and problem-solving skills.",
        [
            "Practice functions and arrays.",
            "Learn classes and objects.",
            "Practice STL and basic data structures."
        ],
        "Build a C++ Quiz Application.",
        "Create a complete C++ console project."
    ),

    "JavaScript": (
        "Medium",
        "1–2 weeks",
        "JavaScript adds interactivity to web applications.",
        [
            "Learn variables, functions and arrays.",
            "Practice DOM manipulation.",
            "Learn events and form handling."
        ],
        "Build an interactive career dashboard.",
        "Create a webpage with JavaScript-based interactions."
    )

}


def generate_learning_roadmap(missing):

    roadmap = []

    for skill in missing:

        if skill in ROADMAP:

            (
                priority,
                time,
                why,
                action,
                project,
                goal
            ) = ROADMAP[skill]

        else:

            priority = "Low"

            time = "1 week"

            why = (
                f"{skill} is relevant to the target job."
            )

            action = [
                f"Learn the basic concepts of {skill}.",
                f"Practice {skill} using small exercises.",
                f"Build a small project using {skill}."
            ]

            project = (
                f"Build a small project using {skill}."
            )

            goal = (
                f"Demonstrate basic practical knowledge of {skill}."
            )

        roadmap.append({

            "skill": skill,

            "priority": priority,

            "time": time,

            "why": why,

            "action": action,

            "project": project,

            "goal": goal

        })

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    roadmap.sort(
        key=lambda item:
        priority_order.get(
            item["priority"],
            3
        )
    )

    for index, item in enumerate(
        roadmap,
        start=1
    ):

        item["order"] = index

    return roadmap


# --------------------------------------------------
# RECOMMENDED PROJECTS
# --------------------------------------------------

PROJECTS = {

    "Python": [
        "Build a Student Performance Analyzer using Python.",
        "Create a Python-based Expense Tracker."
    ],

    "HTML": [
        "Build a responsive student portfolio website.",
        "Create an online resume webpage."
    ],

    "CSS": [
        "Design a responsive portfolio using CSS Flexbox.",
        "Create a responsive career dashboard."
    ],

    "SQL": [
        "Build a College Database Management System.",
        "Create a Student Attendance Database."
    ],

    "Git": [
        "Create a Git-based version-controlled college project.",
        "Practice collaborative development using branches."
    ],

    "GitHub": [
        "Create a professional GitHub portfolio.",
        "Maintain project README files and documentation."
    ],

    "Flask": [
        "Build a Student Management System using Flask.",
        "Create a Flask-based Job Application Tracker."
    ],

    "PDF Processing": [
        "Build a PDF Resume Text Extractor.",
        "Create a Document Analysis application."
    ],

    "OpenAI API": [
        "Build an AI Resume Feedback application.",
        "Create an AI-powered Interview Question Generator."
    ],

    "Machine Learning": [
        "Build a Student Performance Prediction system.",
        "Create a simple Resume Classification model."
    ],

    "Data Analysis": [
        "Build a Student Performance Dashboard.",
        "Create a Resume Skill Analysis system."
    ],

    "MongoDB": [
        "Build a Student Management System using MongoDB.",
        "Create a MongoDB-based Job Application Tracker."
    ],

    "MySQL": [
        "Build a College Database Management System using MySQL.",
        "Create a Student Attendance Management System using MySQL."
    ]

}


def generate_recommended_projects(missing):

    return [

        {
            "skill": skill,
            "projects": PROJECTS[skill]
        }

        for skill in missing
        if skill in PROJECTS

    ]


# --------------------------------------------------
# INTERVIEW QUESTIONS
# --------------------------------------------------

QUESTIONS = {

    "Python": [
        "What are the main features of Python?",
        "What is the difference between a list and a tuple?",
        "What are functions in Python?"
    ],

    "HTML": [
        "What is HTML?",
        "What are semantic HTML elements?",
        "What is the difference between div and section?"
    ],

    "CSS": [
        "What is CSS?",
        "What is Flexbox?",
        "What is responsive web design?"
    ],

    "Flask": [
        "What is Flask?",
        "What is a Flask route?",
        "How do templates work in Flask?"
    ],

    "Git": [
        "What is Git?",
        "What is a Git commit?",
        "What is the difference between git pull and git push?"
    ],

    "GitHub": [
        "What is GitHub?",
        "What is a repository?",
        "How do you push code to GitHub?"
    ],

    "OpenAI API": [
        "What is an API?",
        "How can an API be used in an AI application?",
        "What is prompt engineering?"
    ],

    "PDF Processing": [
        "How can text be extracted from a PDF?",
        "What is PDF processing?",
        "How would you handle a PDF that contains no extractable text?"
    ],

    "Data Analysis": [
        "What is data analysis?",
        "What is data cleaning?",
        "How can data be visualized?"
    ],

    "SQL": [
        "What is SQL?",
        "What is the difference between WHERE and HAVING?",
        "What is a JOIN in SQL?"
    ],

    "MongoDB": [
        "What is MongoDB?",
        "What is a document in MongoDB?",
        "What is the difference between MongoDB and SQL databases?"
    ],

    "MySQL": [
        "What is MySQL?",
        "What is a primary key?",
        "What is a foreign key?"
    ],

    "Machine Learning": [
        "What is machine learning?",
        "What is supervised learning?",
        "What is unsupervised learning?"
    ]

}


def generate_interview_questions(missing):

    result = [

        {
            "topic": skill,
            "questions": QUESTIONS[skill]
        }

        for skill in missing
        if skill in QUESTIONS

    ]

    result.append({

        "topic": "Project",

        "questions": [
            "Explain your AI Career Readiness Analyzer.",
            "Why did you choose this project?",
            "What technologies did you use?",
            "What challenges did you face while building it?"
        ]

    })

    return result


# --------------------------------------------------
# SMART RESUME IMPROVEMENTS
# --------------------------------------------------

def generate_smart_resume_improvements(
    resume_text,
    resume_skills,
    projects,
    job_skills
):

    suggestions = []

    low = resume_text.lower()

    if projects:

        if any(
            len(project.split()) < 12
            for project in projects
        ):

            suggestions.append({

                "title": "Improve project descriptions",

                "description":
                    "Some project descriptions are very short. "
                    "Describe what you built, the technologies used, "
                    "your contribution, and the result.",

                "example":
                    "Use Action + Technology + Contribution + Result."

            })

        project_text = " ".join(
            projects
        ).lower()

        if not any(
            skill.lower() in project_text
            for skill in resume_skills
        ):

            suggestions.append({

                "title":
                    "Mention technologies in projects",

                "description":
                    "Your project descriptions do not clearly show "
                    "which technologies were used.",

                "example":
                    "Example: Developed the application using "
                    "Python, Flask, HTML and CSS."

            })

        contribution_words = [
            "developed",
            "created",
            "designed",
            "implemented",
            "built",
            "integrated",
            "managed"
        ]

        if not any(
            word in project_text
            for word in contribution_words
        ):

            suggestions.append({

                "title":
                    "Show your contribution",

                "description":
                    "Clearly explain what you personally developed "
                    "or implemented in each project.",

                "example":
                    "Use action words such as developed, implemented, "
                    "designed, integrated, tested or built."

            })

        result_words = [
            "improved",
            "reduced",
            "increased",
            "accuracy",
            "users",
            "performance",
            "%",
            "result",
            "faster"
        ]

        if not any(
            word in project_text
            for word in result_words
        ):

            suggestions.append({

                "title":
                    "Add measurable results",

                "description":
                    "Add measurable results wherever possible. "
                    "This makes your project achievements clearer.",

                "example":
                    "Example: Reduced manual resume screening time "
                    "by 40% using automated skill extraction."

            })

    else:

        suggestions.append({

            "title": "Add projects",

            "description":
                "Your resume does not contain clearly detected "
                "project information.",

            "example":
                "Add 2–3 academic or personal projects with "
                "technologies, features, your contribution and results."

        })

    if "github.com" not in low:

        suggestions.append({

            "title":
                "Add GitHub links",

            "description":
                "No GitHub profile or repository link was detected "
                "in the resume.",

            "example":
                "Add your GitHub profile and repository links "
                "for important projects."

        })

    missing = [
        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    if missing:

        suggestions.append({

            "title":
                "Add relevant skills",

            "description":
                "The resume is missing some skills mentioned in "
                "the target job description.",

            "example":
                "Learn or use the missing skills before adding them. "
                "Missing: "
                + ", ".join(missing[:8])
                + "."

        })

    action_words = [
        "developed",
        "created",
        "built",
        "designed",
        "implemented",
        "integrated",
        "analyzed",
        "managed",
        "tested"
    ]

    if not any(
        word in low
        for word in action_words
    ):

        suggestions.append({

            "title":
                "Use strong action words",

            "description":
                "Project and experience descriptions should begin "
                "with clear action words.",

            "example":
                "Use Developed, Built, Designed, Implemented, "
                "Integrated and Analyzed."

        })

    suggestions.append({

        "title":
            "Keep descriptions specific",

        "description":
            "Avoid generic statements such as 'worked on a project' "
            "or 'learned Python'. Explain what you actually built "
            "and your contribution.",

        "example":
            "Use Action + Technology + What you built + Result."

    })

    return suggestions


# --------------------------------------------------
# RESUME STRENGTH / WEAKNESS
# --------------------------------------------------

def generate_resume_strength_weakness_analysis(
    resume_text,
    resume_skills,
    job_skills,
    matching,
    missing,
    education,
    projects,
    certs
):

    strengths = []

    weaknesses = []

    focus = []

    low = resume_text.lower()

    if resume_skills:

        strengths.append(
            "The resume contains identifiable technical or professional skills."
        )

    if matching:

        strengths.append(
            f"The resume matches {len(matching)} skill(s) from the target job."
        )

    if projects:

        strengths.append(
            "Project experience is present in the resume."
        )

    if education:

        strengths.append(
            "Educational information is present and can support the target role."
        )

    if certs:

        strengths.append(
            "Certifications are included and can strengthen the candidate profile."
        )

    if "github.com" in low:

        strengths.append(
            "GitHub links are included in the resume."
        )

    if not resume_skills:

        weaknesses.append(
            "No recognizable skills were detected in the resume."
        )

    elif job_skills and not matching:

        weaknesses.append(
            "No skills from the target job description were detected in the resume."
        )

    elif missing:

        weaknesses.append(
            f"{len(missing)} required job skill(s) are currently missing."
        )

    if not projects:

        weaknesses.append(
            "Project experience was not clearly detected."
        )

    elif any(
        len(project.split()) < 12
        for project in projects
    ):

        weaknesses.append(
            "Some project descriptions are too short and need more detail."
        )

    if "github.com" not in low:

        weaknesses.append(
            "No GitHub profile or repository link was detected."
        )

    if projects:

        project_text = " ".join(
            projects
        ).lower()

        action_words = [
            "developed",
            "created",
            "built",
            "designed",
            "implemented",
            "integrated",
            "analyzed",
            "managed",
            "tested"
        ]

        if not any(
            word in project_text
            for word in action_words
        ):

            weaknesses.append(
                "Project descriptions do not clearly show your individual contribution."
            )

        measurable_words = [
            "%",
            "improved",
            "reduced",
            "increased",
            "accuracy",
            "performance",
            "users",
            "faster"
        ]

        if not any(
            word in project_text
            for word in measurable_words
        ):

            weaknesses.append(
                "Projects do not clearly mention measurable results or impact."
            )

    if missing:

        focus.append(
            "Learn and demonstrate the missing skills required by the target job."
        )

    if projects:

        focus.append(
            "Improve project descriptions using Action + Technology + Contribution + Result."
        )

    else:

        focus.append(
            "Add relevant academic or personal projects."
        )

    if "github.com" not in low:

        focus.append(
            "Add your GitHub profile and important project repositories."
        )

    if education and not certs:

        focus.append(
            "Consider adding relevant certifications or courses."
        )

    if len(weaknesses) <= 2:

        overall = (
            "The resume has a good basic structure, with only a few areas "
            "that need improvement."
        )

    elif len(weaknesses) <= 5:

        overall = (
            "The resume has a reasonable foundation, but several areas "
            "can be improved to better match the target role."
        )

    else:

        overall = (
            "The resume has a basic foundation, but several important "
            "areas should be improved before applying for the target role."
        )

    return {

        "strengths": strengths,

        "weaknesses": weaknesses,

        "areas_to_improve": weaknesses,

        "improvement_focus": focus,

        "overall": overall

    }


# --------------------------------------------------
# FALLBACK AI ANALYSIS
# --------------------------------------------------

def generate_fallback_analysis(
    resume,
    job,
    matching,
    missing
):

    percent = (
        round(
            len(matching) / len(job) * 100
        )
        if job
        else 0
    )

    if percent >= 75:

        readiness = "Advanced"

    elif percent >= 50:

        readiness = "Intermediate"

    else:

        readiness = "Beginner"

    return {

        "career_summary":
            f"Your resume currently matches about {percent}% "
            f"of the detected job skills. You have "
            f"{len(matching)} matching skills and "
            f"{len(missing)} skills that can be improved.",

        "strengths": [
            "You already have some skills required for the target role.",
            "Your resume includes project experience.",
            "Your educational background is relevant to the target role.",
            "You have certifications that can support your profile."
        ],

        "recommendations": [
            "Learn the missing technical skills required by the target job.",
            "Add practical projects that demonstrate the required technologies.",
            "Use Git and GitHub to maintain and showcase your projects.",
            "Improve your resume by clearly describing project impact and technologies used."
        ],

        "readiness_level": readiness

    }


# --------------------------------------------------
# AI ANALYSIS
# --------------------------------------------------

def generate_ai_analysis(
    resume,
    job,
    matching,
    missing
):

    fallback = generate_fallback_analysis(
        resume,
        job,
        matching,
        missing
    )

    if client:

        try:

            prompt = f"""
Resume Skills:
{resume}

Required Job Skills:
{job}

Matching Skills:
{matching}

Missing Skills:
{missing}

Provide a concise career analysis.
Do not invent skills.
"""

            response = client.responses.create(
                model="gpt-5.6",
                input=prompt
            )

            if response.output_text:

                fallback["career_summary"] = (
                    response.output_text
                )

        except Exception as e:

            print(
                "OpenAI API unavailable:",
                e
            )

    return fallback


# --------------------------------------------------
# AI JOB MATCH
# --------------------------------------------------

def generate_ai_job_match(
    resume,
    job,
    projects,
    education,
    certs=None,
    resume_text=""
):

    matching = [
        skill
        for skill in job
        if skill in resume
    ]

    technical = (
        round(
            len(matching) / len(job) * 100
        )
        if job
        else 0
    )

    project_rel = 0

    if projects:

        project_text = " ".join(
            projects
        ).lower()

        coverage = (
            len([
                skill
                for skill in job
                if skill.lower() in project_text
            ])
            / len(job)
            * 100
            if job
            else 0
        )

        quality = 40

        if len(projects) >= 2:

            quality += 20

        if any(
            word in project_text
            for word in [
                "developed",
                "built",
                "created",
                "designed",
                "implemented",
                "integrated",
                "tested"
            ]
        ):

            quality += 15

        if any(
            word in project_text
            for word in [
                "%",
                "improved",
                "reduced",
                "increased",
                "accuracy",
                "performance",
                "users",
                "result"
            ]
        ):

            quality += 15

        if any(
            skill.lower() in project_text
            for skill in resume
        ):

            quality += 10

        project_rel = min(
            round(
                coverage * 0.5
                + quality * 0.5
            ),
            100
        )

    education_rel = 0

    if education:

        education_text = " ".join(
            education
        ).lower()

        if any(
            keyword in education_text
            for keyword in [
                "computer science",
                "information technology",
                "engineering",
                "b.tech",
                "btech",
                "b.e",
                "bachelor"
            ]
        ):

            education_rel = 100

        else:

            education_rel = 70

    soft_skills = [
        "Communication",
        "Teamwork",
        "Problem Solving"
    ]

    soft = round(
        len([
            skill
            for skill in soft_skills
            if skill in resume
        ])
        / 3
        * 100
    )

    cert = 100 if certs else 0

    overall = round(

        technical * 0.45

        + project_rel * 0.25

        + education_rel * 0.10

        + soft * 0.10

        + cert * 0.10

    )

    missing = [
        skill
        for skill in job
        if skill not in resume
    ]

    return {

        "overall_score": overall,

        "technical_skill_match": technical,

        "project_relevance": project_rel,

        "education_relevance": education_rel,

        "soft_skill_match": soft,

        "certification_relevance": cert,

        "matching_skills": matching,

        "missing_skills": missing,

        "matching_summary":
            (
                "Matching skills: "
                + ", ".join(matching)
                if matching
                else
                "No matching job skills were detected."
            ),

        "missing_summary":
            (
                "Skills to improve: "
                + ", ".join(missing)
                if missing
                else
                "No missing skills were detected from the known skill list."
            ),

        "explanation":
            (
                "The resume shows moderate alignment with the target role."
                if overall >= 50
                else
                "The resume currently shows limited alignment with the target role."
            )

    }


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

@app.route(
    "/upload",
    methods=["POST"]
)
def upload():

    resume_file = request.files.get(
        "resume"
    )

    job_description = request.form.get(
        "job_description",
        ""
    )

    if not resume_file:

        return "Please upload a resume PDF."

    if not resume_file.filename.lower().endswith(
        ".pdf"
    ):

        return "Please upload a PDF file."

    file_path = os.path.join(
        UPLOAD_FOLDER,
        resume_file.filename
    )

    resume_file.save(
        file_path
    )

    resume_text = clean_text(
        extract_pdf_text(
            file_path
        )
    )

    resume_skills = extract_skills(
        resume_text
    )

    education = extract_education(
        resume_text
    )

    projects = extract_projects(
        resume_text
    )

    certifications = extract_certifications(
        resume_text
    )

    job_skills = extract_job_skills(
        job_description
    )

    matching_skills = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    missing_skills = generate_skill_gaps(
        resume_skills,
        job_skills
    )

    resume_score = calculate_resume_score(
        resume_skills,
        job_skills,
        education,
        projects,
        certifications
    )

    job_match = calculate_job_match(
        resume_skills,
        job_skills
    )

    ai_analysis = generate_ai_analysis(
        resume_skills,
        job_skills,
        matching_skills,
        missing_skills
    )

    ai_job_match = generate_ai_job_match(
        resume_skills,
        job_skills,
        projects,
        education,
        certifications,
        resume_text
    )

    priority_skill_gaps = (
        generate_priority_skill_gaps(
            missing_skills
        )
    )

    roadmap = generate_learning_roadmap(
        missing_skills
    )

    recommended_projects = (
        generate_recommended_projects(
            missing_skills
        )
    )

    interview_questions = (
        generate_interview_questions(
            missing_skills
        )
    )

    smart_improvements = (
        generate_smart_resume_improvements(
            resume_text,
            resume_skills,
            projects,
            job_skills
        )
    )

    resume_analysis = (
        generate_resume_strength_weakness_analysis(
            resume_text,
            resume_skills,
            job_skills,
            matching_skills,
            missing_skills,
            education,
            projects,
            certifications
        )
    )

    resume_improvement = {

        "missing_skills":
            missing_skills,

        "content_improvements": [

            "Use clear action words when describing your projects.",

            "Mention the technologies used in each project.",

            "Add measurable results wherever possible."

        ],

        "project_improvements": [

            "Explain your individual contribution to each project.",

            "Mention important features and technologies.",

            "Add GitHub links for completed projects."

        ],

        "resume_strengths":
            ai_analysis.get(
                "strengths",
                []
            ),

        "smart_improvements":
            smart_improvements

    }

    return render_template(

        "index.html",

        resume_score=resume_score,

        job_match_score=job_match,

        required_skills=job_skills,

        resume_skills=resume_skills,

        matching_skills=matching_skills,

        missing_skills=missing_skills,

        skill_gaps=missing_skills,

        career_summary=ai_analysis.get(
            "career_summary",
            ""
        ),

        strengths=ai_analysis.get(
            "strengths",
            []
        ),

        recommendations=ai_analysis.get(
            "recommendations",
            []
        ),

        readiness_level=ai_analysis.get(
            "readiness_level",
            "Beginner"
        ),

        ai_job_match=ai_job_match,

        priority_skill_gaps=
            priority_skill_gaps,

        roadmap=roadmap,

        recommended_projects=
            recommended_projects,

        interview_questions=
            interview_questions,

        resume_improvement=
            resume_improvement,

        smart_improvements=
            smart_improvements,

        resume_analysis=
            resume_analysis

    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )