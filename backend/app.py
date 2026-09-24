from flask import Flask, render_template, request

from PyPDF2 import PdfReader

import os
import re

from dotenv import load_dotenv
from openai import OpenAI


# --------------------------------------------------
# FLASK SETUP
# --------------------------------------------------

app = Flask(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = None

if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)


# --------------------------------------------------
# UPLOAD FOLDER
# --------------------------------------------------

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

def extract_pdf_text(pdf_path):

    text = ""

    try:
        reader = PdfReader(pdf_path)

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

    # Remove multiple blank lines
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

    skills = []

    for skill in KNOWN_SKILLS:

        skill_lower = skill.lower()

        if skill_lower in text_lower:
            skills.append(skill)

    return skills


# --------------------------------------------------
# EDUCATION EXTRACTION
# --------------------------------------------------

def extract_education(text):

    education_keywords = [
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

    lines = text.split("\n")

    education = []

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        for keyword in education_keywords:

            if keyword in line_lower:

                education.append(line_clean)

                break

    return education


# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------

def extract_projects(text):

    lines = text.split("\n")

    projects = []

    project_section = False

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        if "project" in line_lower:

            project_section = True

            continue

        if project_section:

            stop_words = [
                "education",
                "certification",
                "experience",
                "skills",
                "achievement",
                "internship",
                "coursework"
            ]

            if any(
                word in line_lower
                for word in stop_words
            ):

                project_section = False

                continue

            if len(line_clean) > 5:

                projects.append(line_clean)

    return projects[:10]


# --------------------------------------------------
# CERTIFICATION EXTRACTION
# --------------------------------------------------

def extract_certifications(text):

    lines = text.split("\n")

    certifications = []

    certification_section = False

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        line_lower = line_clean.lower()

        if (
            "certification" in line_lower
            or "certificate" in line_lower
        ):

            certification_section = True

            continue

        if certification_section:

            stop_words = [
                "education",
                "project",
                "experience",
                "skills",
                "achievement",
                "internship"
            ]

            if any(
                word in line_lower
                for word in stop_words
            ):

                certification_section = False

                continue

            if len(line_clean) > 5:

                certifications.append(line_clean)

    return certifications[:10]


# --------------------------------------------------
# JOB SKILL EXTRACTION
# --------------------------------------------------

def extract_job_skills(job_description):

    text_lower = job_description.lower()

    skills = []

    for skill in KNOWN_SKILLS:

        skill_lower = skill.lower()

        if skill_lower in text_lower:

            skills.append(skill)

    return skills


# --------------------------------------------------
# JOB MATCH
# --------------------------------------------------

def calculate_job_match(
    resume_skills,
    job_skills
):

    if not job_skills:
        return 0

    matching_skills = []

    for skill in job_skills:

        if skill in resume_skills:

            matching_skills.append(skill)

    score = (
        len(matching_skills)
        / len(job_skills)
    ) * 100

    return round(score)


# --------------------------------------------------
# SKILL GAPS
# --------------------------------------------------

def generate_skill_gaps(
    resume_skills,
    job_skills
):

    missing_skills = []

    for skill in job_skills:

        if skill not in resume_skills:

            missing_skills.append(skill)

    return missing_skills


# --------------------------------------------------
# IMPROVED RESUME SCORE
# --------------------------------------------------

def calculate_resume_score(
    resume_skills,
    job_skills,
    education,
    projects,
    certifications
):

    # --------------------------------------------------
    # 1. TECHNICAL SKILLS - 40%
    # --------------------------------------------------

    if resume_skills:

        if job_skills:

            matching_skills = [
                skill
                for skill in job_skills
                if skill in resume_skills
            ]

            technical_percentage = (
                len(matching_skills)
                / len(job_skills)
            ) * 100

        else:

            technical_percentage = 100

    else:

        technical_percentage = 0

    technical_score = (
        technical_percentage * 0.40
    )


    # --------------------------------------------------
    # 2. JOB SKILL MATCH - 25%
    # --------------------------------------------------

    job_match = calculate_job_match(
        resume_skills,
        job_skills
    )

    job_match_score = (
        job_match * 0.25
    )


    # --------------------------------------------------
    # 3. PROJECTS - 15%
    # --------------------------------------------------

    if projects:

        project_percentage = 100

    else:

        project_percentage = 0

    project_score = (
        project_percentage * 0.15
    )


    # --------------------------------------------------
    # 4. EDUCATION - 10%
    # --------------------------------------------------

    if education:

        education_percentage = 100

    else:

        education_percentage = 0

    education_score = (
        education_percentage * 0.10
    )


    # --------------------------------------------------
    # 5. CERTIFICATIONS - 10%
    # --------------------------------------------------

    if certifications:

        certification_percentage = 100

    else:

        certification_percentage = 0

    certification_score = (
        certification_percentage * 0.10
    )


    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    final_score = (
        technical_score
        + job_match_score
        + project_score
        + education_score
        + certification_score
    )

    return round(final_score)


# --------------------------------------------------
# AI JOB MATCH
# --------------------------------------------------

def generate_ai_job_match(
    resume_skills,
    job_skills,
    projects,
    education
):

    matching_skills = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    if job_skills:

        technical_match = round(
            (
                len(matching_skills)
                / len(job_skills)
            ) * 100
        )

    else:

        technical_match = 0


    if projects:

        project_relevance = 70

    else:

        project_relevance = 30


    if education:

        education_relevance = 80

    else:

        education_relevance = 30


    soft_skill_names = [
        "Communication",
        "Teamwork"
    ]

    soft_skill_matches = [
        skill
        for skill in soft_skill_names
        if skill in resume_skills
    ]

    if soft_skill_matches:

        soft_skill_match = round(
            (
                len(soft_skill_matches)
                / len(soft_skill_names)
            ) * 100
        )

    else:

        soft_skill_match = 0


    overall_score = round(
        (
            technical_match
            + project_relevance
            + education_relevance
            + soft_skill_match
        ) / 4
    )


    if technical_match >= 75:

        explanation = (
            "Your resume shows strong technical alignment "
            "with the target role. Continue improving "
            "project depth and practical experience."
        )

    elif technical_match >= 50:

        explanation = (
            "Your resume has a reasonable technical "
            "foundation for the target role, but several "
            "skills can still be improved."
        )

    else:

        explanation = (
            "Your resume has a foundation for the target "
            "role, but several required technical skills "
            "are still missing. Focus on the priority "
            "skill gaps and add practical projects that "
            "demonstrate those skills."
        )


    return {

        "overall_score": overall_score,

        "technical_skill_match": technical_match,

        "project_relevance": project_relevance,

        "education_relevance": education_relevance,

        "soft_skill_match": soft_skill_match,

        "explanation": explanation
    }


# --------------------------------------------------
# PRIORITY SKILL GAPS
# --------------------------------------------------

def generate_priority_skill_gaps(
    missing_skills
):

    priority_gaps = []

    high_priority = [
        "Python",
        "HTML",
        "CSS",
        "Git",
        "GitHub",
        "Flask"
    ]

    medium_priority = [
        "PDF Processing",
        "OpenAI API",
        "Data Analysis",
        "SQL",
        "Machine Learning"
    ]

    reasons = {

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


    for skill in missing_skills:

        if skill in high_priority:

            priority = "High"

        elif skill in medium_priority:

            priority = "Medium"

        else:

            priority = "Low"


        priority_gaps.append({

            "skill": skill,

            "priority": priority,

            "reason": reasons.get(
                skill,
                f"{skill} is relevant to the target job."
            )
        })


    return priority_gaps


# --------------------------------------------------
# PERSONALIZED LEARNING ROADMAP
# --------------------------------------------------

def generate_learning_roadmap(
    missing_skills
):

    roadmap = []

    roadmap_data = {

        "Python": {

            "priority": "High",

            "action": [

                "Learn Python syntax, variables, data types and operators.",

                "Practice functions, lists, dictionaries, loops and file handling.",

                "Build a small Python project such as an expense tracker."
            ],

            "time": "1–2 weeks"
        },


        "HTML": {

            "priority": "High",

            "action": [

                "Learn HTML structure, headings, paragraphs, links and forms.",

                "Practice semantic HTML and form elements.",

                "Build a simple personal portfolio webpage."
            ],

            "time": "4–5 days"
        },


        "CSS": {

            "priority": "High",

            "action": [

                "Learn selectors, properties, box model and positioning.",

                "Practice Flexbox and responsive layouts.",

                "Design a responsive portfolio or career dashboard."
            ],

            "time": "5–7 days"
        },


        "Git": {

            "priority": "High",

            "action": [

                "Learn git init, add, commit, status and log.",

                "Practice branches, merging and resolving conflicts.",

                "Use Git for every project you build."
            ],

            "time": "3–4 days"
        },


        "GitHub": {

            "priority": "High",

            "action": [

                "Create and configure a professional GitHub profile.",

                "Learn repositories, push, pull and branches.",

                "Add README files and documentation to your projects."
            ],

            "time": "2–3 days"
        },


        "Flask": {

            "priority": "High",

            "action": [

                "Learn Flask application structure and routes.",

                "Practice templates, forms and handling POST requests.",

                "Build a small Flask web application."
            ],

            "time": "5–7 days"
        },


        "PDF Processing": {

            "priority": "Medium",

            "action": [

                "Understand how PDF files are structured.",

                "Learn how to extract text from PDFs using PyPDF2.",

                "Build a small PDF text extraction application."
            ],

            "time": "3–4 days"
        },


        "OpenAI API": {

            "priority": "Medium",

            "action": [

                "Understand APIs, API keys and request/response flow.",

                "Learn how to send prompts to an AI API.",

                "Integrate an AI API into a small Flask project."
            ],

            "time": "3–5 days"
        },


        "Data Analysis": {

            "priority": "Medium",

            "action": [

                "Learn basic data cleaning and analysis concepts.",

                "Practice working with structured data.",

                "Build a simple student or resume data analysis project."
            ],

            "time": "5–7 days"
        },


        "SQL": {

            "priority": "Medium",

            "action": [

                "Learn SELECT, INSERT, UPDATE and DELETE.",

                "Practice WHERE, JOIN, GROUP BY and ORDER BY.",

                "Build a small database-based project."
            ],

            "time": "1 week"
        },


        "Machine Learning": {

            "priority": "Medium",

            "action": [

                "Learn basic machine learning concepts.",

                "Study supervised and unsupervised learning.",

                "Build a simple machine learning project."
            ],

            "time": "2–3 weeks"
        },


        "Java": {

            "priority": "Medium",

            "action": [

                "Learn Java syntax, classes and objects.",

                "Practice arrays, strings and collections.",

                "Build a small Java application."
            ],

            "time": "1–2 weeks"
        },


        "C++": {

            "priority": "Medium",

            "action": [

                "Practice C++ syntax and functions.",

                "Learn classes, objects and STL basics.",

                "Build a small C++ project."
            ],

            "time": "1–2 weeks"
        },


        "JavaScript": {

            "priority": "Medium",

            "action": [

                "Learn variables, functions and DOM basics.",

                "Practice events and form handling.",

                "Build an interactive webpage."
            ],

            "time": "1–2 weeks"
        }

    }


    for skill in missing_skills:

        if skill in roadmap_data:

            data = roadmap_data[skill]

            roadmap.append({

                "skill": skill,

                "priority": data["priority"],

                "action": data["action"],

                "time": data["time"]
            })

        else:

            roadmap.append({

                "skill": skill,

                "priority": "Low",

                "action": [

                    f"Learn the basic concepts of {skill}.",

                    f"Practice {skill} using small exercises.",

                    f"Build a small project using {skill}."
                ],

                "time": "1 week"
            })


    return roadmap


# --------------------------------------------------
# RECOMMENDED PROJECTS
# --------------------------------------------------

def generate_recommended_projects(
    missing_skills
):

    project_ideas = {

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


    projects = []

    for skill in missing_skills:

        if skill in project_ideas:

            projects.append({

                "skill": skill,

                "projects": project_ideas[skill]
            })


    return projects


# --------------------------------------------------
# INTERVIEW QUESTIONS
# --------------------------------------------------

def generate_interview_questions(
    missing_skills
):

    question_data = {

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


    interview_questions = []


    for skill in missing_skills:

        if skill in question_data:

            interview_questions.append({

                "topic": skill,

                "questions": question_data[skill]
            })


    interview_questions.append({

        "topic": "Project",

        "questions": [

            "Explain your AI Career Readiness Analyzer.",

            "Why did you choose this project?",

            "What technologies did you use?",

            "What challenges did you face while building it?"
        ]
    })


    return interview_questions


# --------------------------------------------------
# SMART RESUME IMPROVEMENT SUGGESTIONS
# --------------------------------------------------

def generate_smart_resume_improvements(
    resume_text,
    resume_skills,
    projects,
    job_skills
):

    suggestions = []

    text_lower = resume_text.lower()


    # --------------------------------------------------
    # PROJECT DESCRIPTION CHECK
    # --------------------------------------------------

    if projects:

        short_projects = []

        for project in projects:

            words = project.split()

            if len(words) < 12:

                short_projects.append(project)

        if short_projects:

            suggestions.append({

                "title": "Improve project descriptions",

                "description": (
                    "Some project descriptions are very short. "
                    "Describe what you built, the technologies used, "
                    "your contribution, and the result."
                ),

                "example": (
                    "Instead of: 'Created a Python project.' "
                    "Write: 'Developed a Python-based application "
                    "to analyze student performance and generate "
                    "performance insights.'"
                )
            })


        # Check for technology mentions
        project_text = " ".join(projects).lower()

        technology_found = False

        for skill in resume_skills:

            if skill.lower() in project_text:

                technology_found = True

                break

        if not technology_found:

            suggestions.append({

                "title": "Mention technologies in projects",

                "description": (
                    "Your project descriptions do not clearly show "
                    "which technologies were used."
                ),

                "example": (
                    "Example: 'Developed the application using "
                    "Python, Flask, HTML and CSS.'"
                )
            })


        # Contribution check
        contribution_words = [
            "developed",
            "created",
            "designed",
            "implemented",
            "built",
            "developed",
            "integrated",
            "managed"
        ]

        has_contribution_word = any(
            word in project_text
            for word in contribution_words
        )

        if not has_contribution_word:

            suggestions.append({

                "title": "Show your contribution",

                "description": (
                    "Clearly explain what you personally developed "
                    "or implemented in each project."
                ),

                "example": (
                    "Use action words such as developed, implemented, "
                    "designed, integrated, tested or built."
                )
            })


        # Result / impact check
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

        has_result = any(
            word in project_text
            for word in result_words
        )

        if not has_result:

            suggestions.append({

                "title": "Add measurable results",

                "description": (
                    "Add measurable results wherever possible. "
                    "This makes your project achievements clearer."
                ),

                "example": (
                    "Example: 'Reduced manual resume screening time "
                    "by 40% using automated skill extraction.'"
                )
            })

    else:

        suggestions.append({

            "title": "Add projects",

            "description": (
                "Your resume does not contain clearly detected "
                "project information."
            ),

            "example": (
                "Add 2–3 academic or personal projects with "
                "technologies, features, your contribution and results."
            )
        })


    # --------------------------------------------------
    # GITHUB CHECK
    # --------------------------------------------------

    if "github.com" not in text_lower:

        suggestions.append({

            "title": "Add GitHub links",

            "description": (
                "No GitHub profile or repository link was detected "
                "in the resume."
            ),

            "example": (
                "Add your GitHub profile and repository links "
                "for important projects."
            )
        })


    # --------------------------------------------------
    # JOB SKILL CHECK
    # --------------------------------------------------

    missing_job_skills = [

        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    if missing_job_skills:

        suggestions.append({

            "title": "Add relevant skills",

            "description": (
                "The resume is missing some skills mentioned in "
                "the target job description."
            ),

            "example": (
                "Consider adding skills only after you actually "
                "learn or use them. Missing skills include: "
                + ", ".join(missing_job_skills[:8])
                + "."
            )
        })


    # --------------------------------------------------
    # ACTION WORD CHECK
    # --------------------------------------------------

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

    action_word_found = any(
        word in text_lower
        for word in action_words
    )

    if not action_word_found:

        suggestions.append({

            "title": "Use strong action words",

            "description": (
                "Project and experience descriptions should begin "
                "with clear action words."
            ),

            "example": (
                "Use words such as Developed, Built, Designed, "
                "Implemented, Integrated and Analyzed."
            )
        })


    # --------------------------------------------------
    # GENERAL CONTENT CHECK
    # --------------------------------------------------

    suggestions.append({

        "title": "Keep descriptions specific",

        "description": (
            "Avoid generic statements such as 'worked on a project' "
            "or 'learned Python'. Explain what you actually built "
            "and what your contribution was."
        ),

        "example": (
            "Use the structure: Action + Technology + What you built "
            "+ Result."
        )
    })


    return suggestions


# --------------------------------------------------
# FALLBACK AI ANALYSIS
# --------------------------------------------------

def generate_fallback_analysis(
    resume_skills,
    job_skills,
    matching_skills,
    missing_skills
):

    if job_skills:

        match_percentage = round(
            (
                len(matching_skills)
                / len(job_skills)
            ) * 100
        )

    else:

        match_percentage = 0


    if match_percentage >= 75:

        readiness_level = "Advanced"

    elif match_percentage >= 50:

        readiness_level = "Intermediate"

    else:

        readiness_level = "Beginner"


    career_summary = (
        f"Your resume currently matches about "
        f"{match_percentage}% of the detected job skills. "
        f"You have {len(matching_skills)} matching skills "
        f"and {len(missing_skills)} skills that can be improved."
    )


    strengths = [

        "You already have some skills required for the target role.",

        "Your resume includes project experience.",

        "Your educational background is relevant to the target role.",

        "You have certifications that can support your profile."
    ]


    recommendations = [

        "Learn the missing technical skills required by the target job.",

        "Add practical projects that demonstrate the required technologies.",

        "Use Git and GitHub to maintain and showcase your projects.",

        "Improve your resume by clearly describing project impact and technologies used."
    ]


    return {

        "career_summary": career_summary,

        "strengths": strengths,

        "recommendations": recommendations,

        "readiness_level": readiness_level
    }


# --------------------------------------------------
# AI ANALYSIS
# --------------------------------------------------

def generate_ai_analysis(
    resume_skills,
    job_skills,
    matching_skills,
    missing_skills
):

    fallback = generate_fallback_analysis(
        resume_skills,
        job_skills,
        matching_skills,
        missing_skills
    )


    if client:

        try:

            prompt = f"""
You are a career readiness assistant.

Resume Skills:
{resume_skills}

Required Job Skills:
{job_skills}

Matching Skills:
{matching_skills}

Missing Skills:
{missing_skills}

Provide a concise career analysis.

Return:

Career Summary

Strengths

Recommendations

Readiness Level

Do not invent skills that are not present.
"""


            response = client.responses.create(

                model="gpt-5.6",

                input=prompt
            )


            ai_text = response.output_text


            if ai_text:

                fallback["career_summary"] = ai_text


        except Exception as e:

            print(
                "OpenAI API unavailable:",
                e
            )


    return fallback


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.route(
    "/",
    methods=["GET"]
)

def home():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# UPLOAD ROUTE
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


    # --------------------------------------------------
    # SAVE FILE
    # --------------------------------------------------

    file_path = os.path.join(
        UPLOAD_FOLDER,
        resume_file.filename
    )


    resume_file.save(
        file_path
    )


    # --------------------------------------------------
    # EXTRACT RESUME TEXT
    # --------------------------------------------------

    raw_text = extract_pdf_text(
        file_path
    )


    resume_text = clean_text(
        raw_text
    )


    # --------------------------------------------------
    # EXTRACT RESUME INFORMATION
    # --------------------------------------------------

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


    # --------------------------------------------------
    # EXTRACT JOB INFORMATION
    # --------------------------------------------------

    job_skills = extract_job_skills(
        job_description
    )


    # --------------------------------------------------
    # MATCHING SKILLS
    # --------------------------------------------------

    matching_skills = [

        skill

        for skill in job_skills

        if skill in resume_skills
    ]


    missing_skills = generate_skill_gaps(

        resume_skills,

        job_skills
    )


    # --------------------------------------------------
    # IMPROVED RESUME SCORE
    # --------------------------------------------------

    resume_score = calculate_resume_score(

        resume_skills,

        job_skills,

        education,

        projects,

        certifications
    )


    # --------------------------------------------------
    # RULE-BASED JOB MATCH
    # --------------------------------------------------

    job_match = calculate_job_match(

        resume_skills,

        job_skills
    )


    # --------------------------------------------------
    # AI CAREER ANALYSIS
    # --------------------------------------------------

    ai_analysis = generate_ai_analysis(

        resume_skills,

        job_skills,

        matching_skills,

        missing_skills
    )


    # --------------------------------------------------
    # AI JOB MATCH
    # --------------------------------------------------

    ai_job_match = generate_ai_job_match(

        resume_skills,

        job_skills,

        projects,

        education
    )


    # --------------------------------------------------
    # PRIORITY SKILL GAPS
    # --------------------------------------------------

    priority_skill_gaps = generate_priority_skill_gaps(

        missing_skills
    )


    # --------------------------------------------------
    # LEARNING ROADMAP
    # --------------------------------------------------

    roadmap = generate_learning_roadmap(

        missing_skills
    )


    # --------------------------------------------------
    # RECOMMENDED PROJECTS
    # --------------------------------------------------

    recommended_projects = generate_recommended_projects(

        missing_skills
    )


    # --------------------------------------------------
    # INTERVIEW QUESTIONS
    # --------------------------------------------------

    interview_questions = generate_interview_questions(

        missing_skills
    )


    # --------------------------------------------------
    # SMART RESUME IMPROVEMENTS
    # --------------------------------------------------

    smart_improvements = generate_smart_resume_improvements(

        resume_text,

        resume_skills,

        projects,

        job_skills
    )


    # --------------------------------------------------
    # RESUME IMPROVEMENT
    # --------------------------------------------------

    resume_improvement = {

        "missing_skills": missing_skills,

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

        "resume_strengths": ai_analysis.get(

            "strengths",

            []
        ),

        "smart_improvements": smart_improvements
    }


    # --------------------------------------------------
    # RENDER RESULTS
    # --------------------------------------------------

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

        priority_skill_gaps=priority_skill_gaps,

        roadmap=roadmap,

        recommended_projects=recommended_projects,

        interview_questions=interview_questions,

        resume_improvement=resume_improvement,

        smart_improvements=smart_improvements
    )


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )