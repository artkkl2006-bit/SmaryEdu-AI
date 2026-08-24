"""
SMART EDUCATION SYSTEM - COMPLETE V5 (USER-DRIVEN SUBJECTS)
College: Department-based | School: Group-based
Custom Timetable | Differentiated Roadmap
Users can now add their own subjects dynamically.
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
import uuid
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smart-edu-secret-key-2026"

# ============================================================
#  DATA DEFINITIONS
# ============================================================

SCHOOL_GROUPS = {
    "Science_Maths": {
        "name": "Science with Mathematics",
        "subtitle": "Computer Science / Engineering path",
        "careers": ["Software Engineer", "AI/ML Engineer", "Data Scientist",
                    "Civil Engineer", "Mechanical Engineer", "Electronics Engineer"],
        "core_subjects": ["Mathematics", "Physics", "Chemistry", "Computer Science"],
        "importance": {
            "Mathematics": 95, "Physics": 85, "Chemistry": 75,
            "Computer Science": 90, "English": 60, "Biology": 30
        }
    },
    "Science_Biology": {
        "name": "Science with Biology",
        "subtitle": "Medical / Life Sciences path",
        "careers": ["Doctor", "Dentist", "Pharmacist", "Biotechnologist",
                    "Microbiologist", "Biochemist", "Nurse"],
        "core_subjects": ["Biology", "Physics", "Chemistry", "Mathematics"],
        "importance": {
            "Biology": 95, "Chemistry": 85, "Physics": 80,
            "Mathematics": 70, "English": 60, "Computer Science": 30
        }
    },
    "Commerce": {
        "name": "Commerce",
        "subtitle": "Business / Finance / CA path",
        "careers": ["Chartered Accountant", "Business Analyst", "Investment Banker",
                    "Entrepreneur", "Marketing Manager", "Financial Advisor"],
        "core_subjects": ["Accountancy", "Business Studies", "Economics", "Mathematics"],
        "importance": {
            "Accountancy": 95, "Business Studies": 85, "Economics": 90,
            "Mathematics": 80, "English": 65, "Computer Science": 40
        }
    },
    "Arts_Humanities": {
        "name": "Arts & Humanities",
        "subtitle": "Law / Design / Social Sciences path",
        "careers": ["Lawyer", "Graphic Designer", "Psychologist", "Journalist",
                    "Sociologist", "Teacher", "Civil Servant"],
        "core_subjects": ["Political Science", "History", "Economics", "Sociology",
                          "Psychology", "English"],
        "importance": {
            "Political Science": 90, "History": 80, "Economics": 85,
            "Sociology": 75, "Psychology": 80, "English": 85, "Mathematics": 30
        }
    },
    "Vocational": {
        "name": "Vocational / Skill-based",
        "subtitle": "Polytechnic / ITI / Design path",
        "careers": ["Electrician", "Fashion Designer", "Chef",
                    "Automobile Technician", "Graphic Designer"],
        "core_subjects": ["Applied Mathematics", "Applied Science", "English",
                          "Trade Theory", "Practical Skills"],
        "importance": {
            "Applied Mathematics": 80, "Applied Science": 75, "English": 50,
            "Trade Theory": 90, "Practical Skills": 95, "Computer Science": 40
        }
    }
}

COLLEGE_DEPARTMENTS = {
    "CSE": {
        "name": "B.E / B.Tech - Computer Science & Engineering",
        "full_form": "Bachelor of Engineering in Computer Science",
        "careers": ["Software Engineer", "AI/ML Engineer", "Data Scientist",
                    "Full Stack Developer", "DevOps Engineer", "Cloud Architect"],
        "core_subjects": ["Data Structures", "Algorithms", "Operating Systems",
                         "Computer Networks", "Database Systems", "Software Engineering"],
        "lab_subjects": ["Programming Lab", "Web Development Lab", "Database Lab",
                        "Networks Lab", "Project Work"],
        "importance": {
            "Data Structures": 95, "Algorithms": 90, "Operating Systems": 80,
            "Computer Networks": 75, "Database Systems": 85, "Software Engineering": 80,
            "English": 50, "Mathematics": 85
        }
    },
    "ECE": {
        "name": "B.E / B.Tech - Electronics & Communication Engineering",
        "full_form": "Bachelor of Engineering in Electronics & Communication",
        "careers": ["Electronics Engineer", "Embedded Systems Engineer", "VLSI Engineer",
                    "Telecom Engineer", "IoT Specialist"],
        "core_subjects": ["Electronic Devices", "Digital Electronics", "Signals & Systems",
                         "Communication Systems", "Microprocessors", "VLSI Design"],
        "lab_subjects": ["Electronics Lab", "Digital Lab", "Communication Lab",
                        "Microprocessor Lab", "Project Work"],
        "importance": {
            "Electronic Devices": 90, "Digital Electronics": 85, "Signals & Systems": 80,
            "Communication Systems": 85, "Microprocessors": 80, "VLSI Design": 75,
            "English": 50, "Mathematics": 80
        }
    },
    "MECH": {
        "name": "B.E / B.Tech - Mechanical Engineering",
        "full_form": "Bachelor of Engineering in Mechanical Engineering",
        "careers": ["Mechanical Engineer", "Automobile Engineer", "Aerospace Engineer",
                    "Production Engineer", "CAD Engineer"],
        "core_subjects": ["Engineering Mechanics", "Thermodynamics", "Fluid Mechanics",
                         "Machine Design", "Manufacturing Technology", "CAD/CAM"],
        "lab_subjects": ["Mechanics Lab", "Thermodynamics Lab", "Fluid Lab",
                        "CAD Lab", "Workshop Practice"],
        "importance": {
            "Engineering Mechanics": 90, "Thermodynamics": 85, "Fluid Mechanics": 80,
            "Machine Design": 85, "Manufacturing Technology": 80, "CAD/CAM": 75,
            "English": 50, "Mathematics": 80
        }
    },
    "CIVIL": {
        "name": "B.E / B.Tech - Civil Engineering",
        "full_form": "Bachelor of Engineering in Civil Engineering",
        "careers": ["Civil Engineer", "Structural Engineer", "Construction Manager",
                    "Transportation Engineer", "Environmental Engineer"],
        "core_subjects": ["Structural Analysis", "Construction Materials", "Geotechnical Engineering",
                         "Transportation Engineering", "Environmental Engineering", "Surveying"],
        "lab_subjects": ["Materials Lab", "Geotechnical Lab", "Transportation Lab",
                        "Survey Lab", "Project Work"],
        "importance": {
            "Structural Analysis": 90, "Construction Materials": 85, "Geotechnical Engineering": 80,
            "Transportation Engineering": 80, "Environmental Engineering": 75, "Surveying": 85,
            "English": 50, "Mathematics": 80
        }
    },
    "BSC_CS": {
        "name": "B.Sc - Computer Science",
        "full_form": "Bachelor of Science in Computer Science",
        "careers": ["Software Developer", "Web Developer", "Data Analyst",
                    "System Analyst", "IT Support Engineer"],
        "core_subjects": ["Programming in C/C++", "Java Programming", "Database Management",
                         "Web Technologies", "Computer Networks", "Software Engineering"],
        "lab_subjects": ["C++ Lab", "Java Lab", "Web Technology Lab", "DBMS Lab", "Project"],
        "importance": {
            "Programming in C/C++": 90, "Java Programming": 85, "Database Management": 85,
            "Web Technologies": 80, "Computer Networks": 75, "Software Engineering": 80,
            "English": 60, "Mathematics": 75
        }
    },
    "BSC_BIO": {
        "name": "B.Sc - Biology / Life Sciences",
        "full_form": "Bachelor of Science in Life Sciences",
        "careers": ["Biotechnologist", "Microbiologist", "Clinical Research Associate",
                    "Lab Technician", "Environmental Scientist"],
        "core_subjects": ["Cell Biology", "Genetics", "Microbiology", "Biochemistry",
                         "Molecular Biology", "Bioinformatics"],
        "lab_subjects": ["Biology Lab", "Microbiology Lab", "Biochemistry Lab",
                        "Molecular Biology Lab", "Field Study"],
        "importance": {
            "Cell Biology": 90, "Genetics": 85, "Microbiology": 85,
            "Biochemistry": 80, "Molecular Biology": 85, "Bioinformatics": 75,
            "English": 60, "Mathematics": 50
        }
    },
    "BCOM": {
        "name": "B.Com - Commerce",
        "full_form": "Bachelor of Commerce",
        "careers": ["Chartered Accountant", "Financial Analyst", "Investment Banker",
                    "Tax Consultant", "Auditor", "Business Analyst"],
        "core_subjects": ["Financial Accounting", "Corporate Accounting", "Business Law",
                         "Economics", "Taxation", "Auditing"],
        "lab_subjects": ["Accounting Lab (Tally)", "Computerized Accounting", "Project"],
        "importance": {
            "Financial Accounting": 95, "Corporate Accounting": 90, "Business Law": 80,
            "Economics": 85, "Taxation": 85, "Auditing": 80,
            "English": 65, "Mathematics": 60
        }
    },
    "BA": {
        "name": "B.A - Arts / Humanities",
        "full_form": "Bachelor of Arts",
        "careers": ["Lawyer", "Journalist", "Psychologist", "Teacher",
                    "Civil Servant", "Social Worker"],
        "core_subjects": ["Political Science", "History", "Sociology", "Psychology",
                         "Economics", "English Literature"],
        "lab_subjects": ["Research Methodology", "Field Work", "Project Work"],
        "importance": {
            "Political Science": 90, "History": 80, "Sociology": 80,
            "Psychology": 85, "Economics": 85, "English Literature": 80,
            "English": 85, "Mathematics": 30
        }
    },
    "BBA": {
        "name": "BBA - Business Administration",
        "full_form": "Bachelor of Business Administration",
        "careers": ["Business Analyst", "Marketing Manager", "HR Manager",
                    "Entrepreneur", "Management Consultant"],
        "core_subjects": ["Principles of Management", "Marketing Management", "HR Management",
                         "Financial Management", "Business Analytics", "Business Law"],
        "lab_subjects": ["Management Lab", "Business Simulation", "Project Work"],
        "importance": {
            "Principles of Management": 90, "Marketing Management": 85, "HR Management": 80,
            "Financial Management": 85, "Business Analytics": 80, "Business Law": 75,
            "English": 70, "Mathematics": 60
        }
    }
}

SCHOOL_SUBJECTS = [
    "Mathematics", "Science", "Social Science", "English", "Tamil",
    "Hindi", "Computer Science", "Physics", "Chemistry", "Biology"
]

INTEREST_TO_GROUPS = {
    "computers": {
        "label": "Computers & Technology", "keywords": ["computer", "coding", "programming", "gaming", "app", "software",
                     "website", "tech", "gadgets", "ai", "robot", "hacking", "python"],
        "suggested_group": "Science_Maths", "suggested_careers": ["Software Engineer", "AI/ML Engineer", "Data Scientist"], "suggested_department": "CSE"
    },
    "health": {
        "label": "Health & Helping People", "keywords": ["doctor", "hospital", "medicine", "health", "patient", "nurse",
                     "dental", "pharmacy", "biology", "human body", "science lab", "cure"],
        "suggested_group": "Science_Biology", "suggested_careers": ["Doctor", "Pharmacist", "Nurse"], "suggested_department": "BSC_BIO"
    },
    "business": {
        "label": "Business & Money", "keywords": ["business", "money", "finance", "bank", "stock", "invest",
                     "entrepreneur", "startup", "account", "trading", "marketing", "sell"],
        "suggested_group": "Commerce", "suggested_careers": ["Chartered Accountant", "Business Analyst", "Entrepreneur"], "suggested_department": "BCOM"
    },
    "creative": {
        "label": "Arts & Creativity", "keywords": ["draw", "paint", "design", "art", "creative", "music", "dance",
                     "sing", "write", "poem", "story", "act", "film", "photo", "fashion"],
        "suggested_group": "Arts_Humanities", "suggested_careers": ["Graphic Designer", "Journalist", "Psychologist"], "suggested_department": "BA"
    },
    "building": {
        "label": "Building & Making Things", "keywords": ["build", "construct", "engine", "machine", "car", "repair",
                     "electronics", "wiring", "plumbing", "wood", "mechanic", "factory"],
        "suggested_group": "Vocational", "suggested_careers": ["Electrician", "Automobile Technician", "Graphic Designer"], "suggested_department": "MECH"
    },
    "teaching": {
        "label": "Teaching & Social Impact", "keywords": ["teach", "teacher", "professor", "coach", "mentor", "guide",
                     "help", "social", "ngo", "volunteer", "child", "education"],
        "suggested_group": "Arts_Humanities", "suggested_careers": ["Teacher", "Psychologist", "Civil Servant"], "suggested_department": "BA"
    },
    "law": {
        "label": "Law & Justice", "keywords": ["law", "lawyer", "judge", "court", "justice", "police",
                     "legal", "argument", "rights", "constitution", "advocate"],
        "suggested_group": "Arts_Humanities", "suggested_careers": ["Lawyer", "Civil Servant", "Journalist"], "suggested_department": "BA"
    },
    "management": {
        "label": "Management & Leadership", "keywords": ["manage", "leader", "team", "organize", "plan", "strategy",
                     "business", "corporate", "CEO", "manager", "administration"],
        "suggested_group": "Commerce", "suggested_careers": ["Business Analyst", "Marketing Manager", "Entrepreneur"], "suggested_department": "BBA"
    },
    "electronics": {
        "label": "Electronics & Gadgets", "keywords": ["electronic", "circuit", "mobile", "hardware", "chip",
                     "sensor", "robot", "arduino", "embedded", "IoT"],
        "suggested_group": "Science_Maths", "suggested_careers": ["Electronics Engineer", "Embedded Systems Engineer"], "suggested_department": "ECE"
    }
}

SKILL_DATABASE = {
    "Python": {"domain": "Programming", "courses": ["CS50P - Harvard", "Automate the Boring Stuff", "Python for Everybody"], "projects": ["CLI Calculator", "Weather App", "Web Scraper"], "practice": ["Leetcode Easy", "HackerRank Python"]},
    "Java": {"domain": "Programming", "courses": ["Java Programming Masterclass", "Head First Java"], "projects": ["Banking System", "Student Management System"], "practice": ["CodeChef Java", "HackerRank Java"]},
    "Data_Analysis": {"domain": "Data Science", "courses": ["Data Analysis with Python", "SQL for Data Analysis"], "projects": ["Sales Dashboard", "Customer Segmentation"], "practice": ["Kaggle Datasets", "SQLZoo"]},
    "Machine_Learning": {"domain": "AI/ML", "courses": ["Andrew Ng ML Course", "FastAI"], "projects": ["Spam Classifier", "Price Predictor"], "practice": ["Kaggle Competitions", "Scikit-learn Docs"]},
    "Web_Dev": {"domain": "Web Development", "courses": ["The Odin Project", "Full Stack Open"], "projects": ["Portfolio Website", "E-commerce Site", "Blog App"], "practice": ["Frontend Mentor", "FreeCodeCamp"]},
    "Communication": {"domain": "Soft Skills", "courses": ["Effective Communication", "Public Speaking"], "projects": ["Debate Club", "Presentation Series"], "practice": ["Toastmasters", "Daily Journaling"]},
    "Leadership": {"domain": "Soft Skills", "courses": ["Leadership Principles", "Team Management"], "projects": ["Student Club Lead", "Event Organisation"], "practice": ["Volunteer Coordination", "Peer Mentoring"]},
    "Accounting": {"domain": "Finance", "courses": ["Financial Accounting", "Tally ERP"], "projects": ["Budget Tracker", "Invoice System"], "practice": ["Tally Practice", "Balance Sheet Exercises"]},
    "Design": {"domain": "Creative", "courses": ["UI/UX Design", "Canva Masterclass"], "projects": ["App Mockup", "Brand Kit Design"], "practice": ["Dribbble Challenges", "Daily UI"]},
    "Biology_Lab": {"domain": "Life Sciences", "courses": ["Lab Techniques", "Bioinformatics Basics"], "projects": ["Lab Report Analysis", "DNA Sequence Tool"], "practice": ["Virtual Labs", "NEET Practice"]},
    "Clinical_Skills": {"domain": "Medical", "courses": ["Clinical Procedures", "Patient Care Basics"], "projects": ["Case Study Analysis", "Diagnosis Flowchart"], "practice": ["OSCE Practice", "Medical Terminology"]},
    "Financial_Analysis": {"domain": "Finance", "courses": ["Financial Modeling", "Investment Analysis"], "projects": ["Stock Portfolio Tracker", "Financial Report"], "practice": ["Bloomberg Terminal", "Yahoo Finance API"]},
    "Communication_Systems": {"domain": "Electronics", "courses": ["Digital Communication", "Wireless Systems"], "projects": ["FM Transmitter", "Signal Analyzer"], "practice": ["MATLAB Simulations", "Circuit Design"]},
    "CAD_Design": {"domain": "Engineering", "courses": ["AutoCAD Masterclass", "SolidWorks Basics"], "projects": ["3D Model of a Building", "Machine Part Design"], "practice": ["CAD Challenges", "3D Printing Prep"]},
    "Research_Methodology": {"domain": "Academics", "courses": ["Research Methods", "Academic Writing"], "projects": ["Literature Review", "Research Proposal"], "practice": ["Journal Reading", "Conference Presentations"]}
}

CAREER_TO_SKILLS = {
    "Software Engineer": ["Python", "Java", "Web_Dev", "Communication"],
    "AI/ML Engineer": ["Python", "Machine_Learning", "Data_Analysis", "Communication"],
    "Data Scientist": ["Python", "Data_Analysis", "Machine_Learning", "Communication"],
    "Doctor": ["Biology_Lab", "Clinical_Skills", "Communication", "Leadership"],
    "Chartered Accountant": ["Accounting", "Financial_Analysis", "Communication", "Leadership"],
    "Lawyer": ["Communication", "Leadership", "Research_Methodology"],
    "Graphic Designer": ["Design", "Communication", "Web_Dev"],
    "Entrepreneur": ["Leadership", "Communication", "Web_Dev", "Accounting"],
    "Civil Engineer": ["CAD_Design", "Web_Dev", "Communication"],
    "Teacher": ["Communication", "Leadership", "Research_Methodology"],
    "Pharmacist": ["Biology_Lab", "Communication"],
    "Mechanical Engineer": ["CAD_Design", "Python", "Web_Dev"],
    "Business Analyst": ["Data_Analysis", "Communication", "Leadership"],
    "Psychologist": ["Communication", "Leadership", "Research_Methodology"],
    "Fashion Designer": ["Design", "Communication"],
    "Electrician": ["Web_Dev", "Communication"],
    "Automobile Technician": ["CAD_Design", "Communication"],
    "Journalist": ["Communication", "Leadership", "Research_Methodology"],
    "Nurse": ["Biology_Lab", "Clinical_Skills", "Communication"],
    "Microbiologist": ["Biology_Lab", "Data_Analysis", "Research_Methodology"],
    "Biotechnologist": ["Biology_Lab", "Python", "Data_Analysis"],
    "Marketing Manager": ["Communication", "Data_Analysis", "Leadership"],
    "Financial Advisor": ["Accounting", "Financial_Analysis", "Communication"],
    "Investment Banker": ["Accounting", "Financial_Analysis", "Data_Analysis"],
    "Civil Servant": ["Communication", "Leadership", "Data_Analysis"],
    "Dentist": ["Biology_Lab", "Clinical_Skills", "Communication"],
    "Chef": ["Design", "Leadership"],
    "Electronics Engineer": ["Communication_Systems", "Python", "CAD_Design"],
    "Embedded Systems Engineer": ["Python", "Communication_Systems", "Web_Dev"],
    "Full Stack Developer": ["Python", "Java", "Web_Dev", "Communication"],
    "DevOps Engineer": ["Python", "Web_Dev", "Communication", "Leadership"],
    "Cloud Architect": ["Python", "Web_Dev", "Leadership", "Communication"],
    "Structural Engineer": ["CAD_Design", "Communication", "Leadership"],
    "Construction Manager": ["Leadership", "Communication", "CAD_Design"],
    "Software Developer": ["Python", "Java", "Web_Dev", "Communication"],
    "Data Analyst": ["Data_Analysis", "Python", "Communication"],
    "System Analyst": ["Data_Analysis", "Communication", "Leadership"],
    "Clinical Research Associate": ["Biology_Lab", "Research_Methodology", "Communication"],
    "Lab Technician": ["Biology_Lab", "Data_Analysis", "Communication"],
    "Environmental Scientist": ["Biology_Lab", "Data_Analysis", "Research_Methodology"],
    "Tax Consultant": ["Accounting", "Financial_Analysis", "Communication"],
    "Auditor": ["Accounting", "Financial_Analysis", "Communication"],
    "Social Worker": ["Communication", "Leadership", "Research_Methodology"],
    "HR Manager": ["Communication", "Leadership", "Data_Analysis"],
    "Management Consultant": ["Leadership", "Communication", "Data_Analysis"],
    "VLSI Engineer": ["Communication_Systems", "CAD_Design", "Python"],
    "IoT Specialist": ["Python", "Web_Dev", "Communication_Systems"],
    "Aerospace Engineer": ["CAD_Design", "Python", "Communication"],
    "Production Engineer": ["CAD_Design", "Leadership", "Communication"]
}

# ============================================================
#  CORE ENGINE FUNCTIONS
# ============================================================

def recommend_school_group(career_interest):
    ci_lower = career_interest.lower()
    scores = {}
    for gkey, gdata in SCHOOL_GROUPS.items():
        score = 0
        for career in gdata["careers"]:
            if ci_lower in career.lower():
                score += 10
            for word in career.lower().split():
                if word in ci_lower and len(word) > 2:
                    score += 5
        for subj in gdata["core_subjects"]:
            if subj.lower() in ci_lower:
                score += 3
        if score > 0:
            scores[gkey] = score
    if not scores:
        return None
    return max(scores, key=scores.get)

def recommend_college_department(career_interest):
    ci_lower = career_interest.lower()
    scores = {}
    for dkey, ddata in COLLEGE_DEPARTMENTS.items():
        score = 0
        for career in ddata["careers"]:
            if ci_lower in career.lower():
                score += 10
            for word in career.lower().split():
                if word in ci_lower and len(word) > 2:
                    score += 5
        for subj in ddata["core_subjects"]:
            if subj.lower() in ci_lower:
                score += 3
        if score > 0:
            scores[dkey] = score
    if not scores:
        return None
    return max(scores, key=scores.get)

def recommend_from_interests(interest_text, is_college=False):
    it_lower = interest_text.lower()
    scores = {}
    for ikey, idata in INTEREST_TO_GROUPS.items():
        score = 0
        for kw in idata["keywords"]:
            if kw in it_lower:
                score += 3
        if score > 0:
            scores[ikey] = {"score": score, "data": idata}
    if not scores:
        return None
    best_key = max(scores, key=lambda k: scores[k]["score"])
    best = scores[best_key]["data"]

    if is_college:
        dept_key = best.get("suggested_department", "CSE")
        dept = COLLEGE_DEPARTMENTS[dept_key]
        return {
            "interest_category": best["label"],
            "is_college": True,
            "department_key": dept_key,
            "department_name": dept["name"],
            "full_form": dept["full_form"],
            "suggested_careers": best["suggested_careers"],
            "all_careers": dept["careers"],
            "core_subjects": dept["core_subjects"],
            "lab_subjects": dept.get("lab_subjects", [])
        }
    else:
        group_key = best["suggested_group"]
        group = SCHOOL_GROUPS[group_key]
        return {
            "interest_category": best["label"],
            "is_college": False,
            "group_key": group_key,
            "group_name": group["name"],
            "group_subtitle": group["subtitle"],
            "suggested_careers": best["suggested_careers"],
            "all_careers": group["careers"],
            "core_subjects": group["core_subjects"]
        }

def get_subject_importance_school(recommended_group, scores, user_subjects=None, user_importance=None):
    """Return subject importance — uses user subjects if provided, else falls back to group."""
    if user_subjects and len(user_subjects) > 0:
        result = []
        for subj in user_subjects:
            imp = user_importance.get(subj, 50) if user_importance else 50
            scored = scores.get(subj, None)
            priority = "High" if imp >= 80 else ("Medium" if imp >= 50 else "Low")
            result.append({"subject": subj, "importance": imp, "priority": priority, "your_score": scored})
        result.sort(key=lambda x: x["importance"], reverse=True)
        return result
    # Fallback to group default
    if not recommended_group or recommended_group not in SCHOOL_GROUPS:
        return []
    group = SCHOOL_GROUPS[recommended_group]
    result = []
    for subj, imp in group["importance"].items():
        scored = scores.get(subj, None)
        priority = "High" if imp >= 80 else ("Medium" if imp >= 50 else "Low")
        result.append({"subject": subj, "importance": imp, "priority": priority, "your_score": scored})
    result.sort(key=lambda x: x["importance"], reverse=True)
    return result

def get_subject_importance_college(department, scores, user_subjects=None, user_importance=None):
    """Return subject importance — uses user subjects if provided, else falls back to department."""
    if user_subjects and len(user_subjects) > 0:
        result = []
        for subj in user_subjects:
            imp = user_importance.get(subj, 50) if user_importance else 50
            scored = scores.get(subj, None)
            priority = "High" if imp >= 80 else ("Medium" if imp >= 50 else "Low")
            result.append({"subject": subj, "importance": imp, "priority": priority, "your_score": scored})
        result.sort(key=lambda x: x["importance"], reverse=True)
        return result
    # Fallback to department default
    if not department or department not in COLLEGE_DEPARTMENTS:
        return []
    dept = COLLEGE_DEPARTMENTS[department]
    result = []
    for subj, imp in dept["importance"].items():
        scored = scores.get(subj, None)
        priority = "High" if imp >= 80 else ("Medium" if imp >= 50 else "Low")
        result.append({"subject": subj, "importance": imp, "priority": priority, "your_score": scored})
    result.sort(key=lambda x: x["importance"], reverse=True)
    return result

def get_subjects_for_student(student):
    """Return subjects — prefers user_subjects if set, otherwise falls back to group/department."""
    user_subjects = student.get("user_subjects", [])
    if user_subjects and len(user_subjects) > 0:
        return user_subjects
    is_college = student.get("student_type") == "college"
    if is_college:
        dept_key = student.get("recommended_group", "")
        if dept_key in COLLEGE_DEPARTMENTS:
            dept = COLLEGE_DEPARTMENTS[dept_key]
            return dept["core_subjects"] + dept.get("lab_subjects", [])
        return ["Data Structures", "Algorithms", "Programming", "English", "Mathematics"]
    else:
        group_key = student.get("recommended_group", "")
        if group_key in SCHOOL_GROUPS:
            return SCHOOL_GROUPS[group_key]["core_subjects"]
        return SCHOOL_SUBJECTS

def analyze_skill_gaps(selected_career, skills, is_college=False):
    if not selected_career or selected_career not in CAREER_TO_SKILLS:
        return []
    needed_skills = CAREER_TO_SKILLS[selected_career]
    target = 5 if not is_college else 7
    gaps = []
    for sk in needed_skills:
        current = skills.get(sk, 0)
        if current < target:
            gap_size = target - current
            skill_info = SKILL_DATABASE.get(sk, {})
            if is_college:
                status = "Critical" if gap_size >= 5 else ("Moderate" if gap_size >= 3 else "Minor")
            else:
                status = "Learn" if gap_size >= 3 else "Improve"
            gaps.append({
                "skill": sk.replace("_", " "),
                "domain": skill_info.get("domain", ""),
                "current_level": current,
                "target_level": target,
                "gap": gap_size,
                "status": status
            })
    gaps.sort(key=lambda x: x["gap"], reverse=True)
    return gaps

def get_recommendations(selected_career, skills, is_college=False):
    gaps = analyze_skill_gaps(selected_career, skills, is_college)
    recs = {"courses": [], "projects": [], "practice": []}
    for g in gaps:
        skill_key = g["skill"].replace(" ", "_")
        skill_info = SKILL_DATABASE.get(skill_key, {})
        for course in skill_info.get("courses", []):
            if course not in recs["courses"]:
                recs["courses"].append(course)
        for proj in skill_info.get("projects", []):
            if proj not in recs["projects"]:
                recs["projects"].append(proj)
        for prac in skill_info.get("practice", []):
            if prac not in recs["practice"]:
                recs["practice"].append(prac)
    return recs

def get_skills_for_career(selected_career):
    if selected_career and selected_career in CAREER_TO_SKILLS:
        return CAREER_TO_SKILLS[selected_career]
    return list(SKILL_DATABASE.keys())

def get_careers_for_student(student):
    is_college = student.get("student_type") == "college"
    rg = student.get("recommended_group", "")
    if is_college and rg in COLLEGE_DEPARTMENTS:
        return COLLEGE_DEPARTMENTS[rg]["careers"]
    elif not is_college and rg in SCHOOL_GROUPS:
        return SCHOOL_GROUPS[rg]["careers"]
    return list(CAREER_TO_SKILLS.keys())

# ============================================================
#  DATA FILE STORAGE
# ============================================================

DATA_FILE = "students_data.json"

def load_all():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_all(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================
#  ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# --- AUTH ---

@app.route("/api/register", methods=["POST"])
def register():
    data = load_all()
    email = request.json.get("email", "").strip().lower()
    password = request.json.get("password", "")
    name = request.json.get("name", "").strip()
    grade = request.json.get("grade", request.json.get("education_level", "10"))

    if not email or not password or not name:
        return jsonify({"error": "All fields required"}), 400

    for sid, s in data.items():
        if s.get("email") == email:
            return jsonify({"error": "Email already registered. Please login."}), 400

    if grade == "school":
        grade = "10"
    elif grade == "college":
        grade = "College"

    is_college = grade in ["College", "College_PG", "11", "12"]

    group = request.json.get("group", "")
    dept = request.json.get("dept", "")
    interest = request.json.get("interest", "")

    sid = str(uuid.uuid4())[:8]
    data[sid] = {
        "email": email,
        "password": hash_password(password),
        "name": name,
        "grade": grade,
        "student_type": "college" if is_college else "school",
        "education_level": grade,
        "career_interest": interest,
        "recommended_group": group if (not is_college) else dept,
        "selected_career": "",
        "scores": {},
        "score_type": "marks" if grade == "10" else "cgpa",
        "attendance": {},
        "custom_timetable": [],
        "assignments": [],
        "exams": [],
        "skills": {},
        "profile_completed": False,
        "created_at": datetime.now().isoformat(),
        # NEW: user-managed subjects
        "user_subjects": [],
        "user_subject_importance": {}
    }
    save_all(data)
    session["student_id"] = sid
    return jsonify({
        "id": sid,
        "name": name,
        "message": "Registration successful!",
        "education_level": "college" if is_college else "school"
    })


@app.route("/api/login", methods=["POST"])
def login():
    data = load_all()
    email = request.json.get("email", "").strip().lower()
    password = request.json.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    for sid, s in data.items():
        if s.get("email") == email and s.get("password") == hash_password(password):
            session["student_id"] = sid
            return jsonify({
                "authenticated": True,
                "user": {
                    "id": sid,
                    "name": s["name"],
                    "email": s.get("email", ""),
                    "profile_completed": s.get("profile_completed", False),
                    "education_level": s.get("student_type", "school"),
                    "grade": s.get("grade", ""),
                    "career": s.get("selected_career", "")
                },
                "message": "Login successful!"
            })
    return jsonify({"error": "Invalid email or password"}), 401


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.pop("student_id", None)
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/check")
def check_auth():
    sid = session.get("student_id")
    if not sid:
        return jsonify({"authenticated": False})
    data = load_all()
    if sid not in data:
        session.pop("student_id", None)
        return jsonify({"authenticated": False})
    s = data[sid]
    return jsonify({
        "authenticated": True,
        "user": {
            "id": sid,
            "name": s["name"],
            "email": s.get("email", ""),
            "profile_completed": s.get("profile_completed", False),
            "education_level": s.get("student_type", "school"),
            "grade": s.get("grade", ""),
            "career": s.get("selected_career", "")
        }
    })


# --- PROFILE ---

@app.route("/api/profile", methods=["POST"])
def save_profile():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    name = request.json.get("name", "").strip()
    grade = request.json.get("grade", "").strip()
    if not name or not grade:
        return jsonify({"error": "Name and grade required"}), 400
    is_college = grade in ["College", "College_PG", "11", "12"]
    data[sid]["name"] = name
    data[sid]["grade"] = grade
    data[sid]["student_type"] = "college" if is_college else "school"
    data[sid]["score_type"] = "marks" if grade == "10" else "cgpa"
    data[sid]["profile_completed"] = True
    save_all(data)
    return jsonify({"message": "Profile saved!", "name": name, "grade": grade,
                    "student_type": data[sid]["student_type"], "score_type": data[sid]["score_type"]})


# --- STUDENT DATA ---

@app.route("/api/student")
def get_student():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    s_copy = {k: v for k, v in s.items() if k != "password"}
    return jsonify({"student": s_copy})


# --- USER SUBJECTS (NEW) ---

@app.route("/api/user-subjects", methods=["GET", "POST"])
def api_user_subjects():
    """GET: Return user's custom subjects + importance. POST: Save user subjects + importance."""
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    if request.method == "POST":
        subjects = request.json.get("subjects", [])
        importance = request.json.get("importance", {})
        # Clean: keep only non-empty subject names
        subjects = [s.strip() for s in subjects if s.strip()]
        data[sid]["user_subjects"] = subjects
        data[sid]["user_subject_importance"] = importance
        save_all(data)
        return jsonify({
            "message": f"{len(subjects)} subjects saved!",
            "user_subjects": subjects,
            "user_subject_importance": importance
        })

    s = data[sid]
    return jsonify({
        "user_subjects": s.get("user_subjects", []),
        "user_subject_importance": s.get("user_subject_importance", {}),
        "using_custom": len(s.get("user_subjects", [])) > 0
    })


# --- RECOMMENDATIONS ---

@app.route("/api/recommend-career", methods=["POST"])
def api_recommend_career():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    s = data[sid]
    is_college = s.get("student_type") == "college"
    career = request.json.get("career", "").strip()

    if not career:
        return jsonify({"error": "Career interest is required"}), 400

    if is_college:
        dept_key = recommend_college_department(career)
        if not dept_key:
            return jsonify({"error": "Could not determine department. Try a more specific career."}), 400
        dept = COLLEGE_DEPARTMENTS[dept_key]
        s["career_interest"] = career
        s["recommended_group"] = dept_key
        if not s.get("selected_career"):
            s["selected_career"] = dept["careers"][0]
        save_all(data)
        return jsonify({
            "is_college": True,
            "department_key": dept_key,
            "department_name": dept["name"],
            "full_form": dept["full_form"],
            "careers": dept["careers"],
            "core_subjects": dept["core_subjects"],
            "lab_subjects": dept.get("lab_subjects", []),
            "suggested_career": s["selected_career"]
        })
    else:
        group_key = recommend_school_group(career)
        if not group_key:
            return jsonify({"error": "Could not determine group. Try a more specific career."}), 400
        group = SCHOOL_GROUPS[group_key]
        s["career_interest"] = career
        s["recommended_group"] = group_key
        if not s.get("selected_career"):
            s["selected_career"] = group["careers"][0]
        save_all(data)
        return jsonify({
            "is_college": False,
            "group_key": group_key,
            "group_name": group["name"],
            "group_subtitle": group["subtitle"],
            "careers": group["careers"],
            "core_subjects": group["core_subjects"],
            "suggested_career": s["selected_career"]
        })


@app.route("/api/recommend-from-interests", methods=["POST"])
def api_recommend_from_interests():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    s = data[sid]
    is_college = s.get("student_type") == "college"
    interests = request.json.get("interests", "").strip()

    if not interests:
        return jsonify({"error": "Please tell us about your interests"}), 400

    result = recommend_from_interests(interests, is_college)
    if not result:
        return jsonify({"error": "Could not identify interest area. Try describing in more detail."}), 400

    s["career_interest"] = f"Interested in: {interests}"
    if is_college:
        s["recommended_group"] = result["department_key"]
        s["selected_career"] = result["suggested_careers"][0]
    else:
        s["recommended_group"] = result["group_key"]
        s["selected_career"] = result["suggested_careers"][0]
    save_all(data)
    return jsonify(result)


@app.route("/api/recommend-career-from-subjects", methods=["POST"])
def api_recommend_career_from_subjects():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    s = data[sid]
    is_college = s.get("student_type") == "college"
    subjects = request.json.get("subjects", [])

    if not subjects or len(subjects) == 0:
        return jsonify({"error": "Please enter at least one subject"}), 400

    subjects = [s.strip().lower() for s in subjects if s.strip()]

    if is_college:
        dept_scores = {}
        for dkey, ddata in COLLEGE_DEPARTMENTS.items():
            score = 0
            all_dept_subjects = [s.lower() for s in ddata["core_subjects"]]
            all_dept_subjects += [s.lower() for s in ddata.get("lab_subjects", [])]
            for us in subjects:
                for ds in all_dept_subjects:
                    if us in ds or ds in us:
                        score += 2
            if score > 0:
                dept_scores[dkey] = score

        if not dept_scores:
            return jsonify({"error": "Could not match your subjects to any department. Try different subjects."}), 400

        best_dept_key = max(dept_scores, key=dept_scores.get)
        dept = COLLEGE_DEPARTMENTS[best_dept_key]

        career_scores = {}
        for career in dept["careers"]:
            score = 0
            cl = career.lower()
            for us in subjects:
                for word in cl.split():
                    if us in word or word in us:
                        score += 1
            career_scores[career] = score

        best_career = max(career_scores, key=career_scores.get) if max(career_scores.values()) > 0 else dept["careers"][0]

        s["recommended_group"] = best_dept_key
        s["selected_career"] = best_career
        s["career_interest"] = f"Subjects: {', '.join(subjects)}"
        save_all(data)

        return jsonify({
            "is_college": True,
            "department_key": best_dept_key,
            "department_name": dept["name"],
            "full_form": dept["full_form"],
            "recommended_career": best_career,
            "all_careers": dept["careers"],
            "core_subjects": dept["core_subjects"],
            "lab_subjects": dept.get("lab_subjects", []),
            "match_score": dept_scores[best_dept_key]
        })
    else:
        group_scores = {}
        for gkey, gdata in SCHOOL_GROUPS.items():
            score = 0
            all_group_subjects = [s.lower() for s in gdata["core_subjects"]]
            for us in subjects:
                for gs in all_group_subjects:
                    if us in gs or gs in us:
                        score += 2
            if score > 0:
                group_scores[gkey] = score

        if not group_scores:
            return jsonify({"error": "Could not match your subjects to any group. Try different subjects."}), 400

        best_group_key = max(group_scores, key=group_scores.get)
        group = SCHOOL_GROUPS[best_group_key]

        career_scores = {}
        for career in group["careers"]:
            score = 0
            cl = career.lower()
            for us in subjects:
                for word in cl.split():
                    if us in word or word in us:
                        score += 1
            career_scores[career] = score

        best_career = max(career_scores, key=career_scores.get) if max(career_scores.values()) > 0 else group["careers"][0]

        s["recommended_group"] = best_group_key
        s["selected_career"] = best_career
        s["career_interest"] = f"Subjects: {', '.join(subjects)}"
        save_all(data)

        return jsonify({
            "is_college": False,
            "group_key": best_group_key,
            "group_name": group["name"],
            "group_subtitle": group["subtitle"],
            "recommended_career": best_career,
            "all_careers": group["careers"],
            "core_subjects": group["core_subjects"],
            "match_score": group_scores[best_group_key]
        })


# --- SUBJECTS ---

@app.route("/api/subjects-for-user")
def api_subjects_for_user():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    subjects = get_subjects_for_student(s)
    return jsonify({"subjects": subjects, "using_custom": len(s.get("user_subjects", [])) > 0})


@app.route("/api/student-subjects")
def api_student_subjects():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    subjects = get_subjects_for_student(s)
    is_college = s.get("student_type") == "college"
    return jsonify({
        "subjects": subjects,
        "student_type": s.get("student_type", "school"),
        "score_type": s.get("score_type", "marks"),
        "grade": s.get("grade", ""),
        "is_college": is_college,
        "recommended_group": s.get("recommended_group", ""),
        "using_custom": len(s.get("user_subjects", [])) > 0,
        "group_or_dept_name": COLLEGE_DEPARTMENTS[s["recommended_group"]]["name"]
            if (is_college and s.get("recommended_group") in COLLEGE_DEPARTMENTS)
            else (SCHOOL_GROUPS[s["recommended_group"]]["name"]
                  if (not is_college and s.get("recommended_group") in SCHOOL_GROUPS)
                  else "")
    })


# --- ACADEMICS ---

@app.route("/api/academics", methods=["GET", "POST"])
def api_academics():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]

    if request.method == "POST":
        subject = request.json.get("subject", "").strip()
        marks = request.json.get("marks", 0)
        if not subject:
            return jsonify({"error": "Subject is required"}), 400
        if s.get("student_type") == "college" and (marks < 0 or marks > 10):
            return jsonify({"error": "CGPA must be between 0 and 10"}), 400
        if s.get("student_type") != "college" and (marks < 0 or marks > 100):
            return jsonify({"error": "Marks must be between 0 and 100"}), 400
        s["scores"][subject] = marks
        save_all(data)
        return jsonify({"message": "Saved!", "scores": s["scores"]})

    return jsonify({"scores": s.get("scores", {}), "score_type": s.get("score_type", "marks")})


# --- SUBJECT IMPORTANCE (UPDATED to use user subjects) ---

@app.route("/api/subject-importance")
def api_subject_importance():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    is_college = s.get("student_type") == "college"
    group_or_dept = s.get("recommended_group", "")
    user_subjects = s.get("user_subjects", [])
    user_importance = s.get("user_subject_importance", {})

    if is_college:
        imp = get_subject_importance_college(group_or_dept, s.get("scores", {}), user_subjects, user_importance)
        name = COLLEGE_DEPARTMENTS[group_or_dept]["name"] if group_or_dept in COLLEGE_DEPARTMENTS else ""
    else:
        imp = get_subject_importance_school(group_or_dept, s.get("scores", {}), user_subjects, user_importance)
        name = SCHOOL_GROUPS[group_or_dept]["name"] if group_or_dept in SCHOOL_GROUPS else ""

    return jsonify({
        "importance": imp,
        "group_name": name,
        "career_interest": s.get("career_interest", ""),
        "is_college": is_college,
        "score_type": s.get("score_type", "marks"),
        "using_custom": len(user_subjects) > 0
    })


# --- ATTENDANCE (already works with any subject keys) ---

@app.route("/api/attendance", methods=["GET", "POST"])
def api_attendance():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    if request.method == "POST":
        records = request.json.get("records", {})
        for subj, present in records.items():
            if subj not in data[sid]["attendance"]:
                data[sid]["attendance"][subj] = []
            data[sid]["attendance"][subj].append(present)
        save_all(data)
        return jsonify({"message": "Attendance marked!"})

    s = data[sid]
    is_college = s.get("student_type") == "college"
    att = s.get("attendance", {})
    result = {}
    warnings = []
    for subj, recs in att.items():
        if recs:
            pct = round((sum(recs) / len(recs)) * 100, 1)
        else:
            pct = 0
        result[subj] = {"percentage": pct, "total": len(recs), "present": sum(recs)}
        if is_college and pct < 75 and pct > 0:
            warnings.append({
                "subject": subj, "percentage": pct,
                "message": f"Warning: {subj} attendance is {pct}% (below 75% minimum!)"
            })
    return jsonify({
        "attendance": result, "warnings": warnings,
        "is_college": is_college
    })


# --- CUSTOM TIMETABLE ---

@app.route("/api/custom-timetable", methods=["GET", "POST"])
def custom_timetable():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401

    if request.method == "POST":
        entries = request.json.get("entries", [])
        data[sid]["custom_timetable"] = entries
        save_all(data)
        return jsonify({"message": "Timetable saved!", "count": len(entries)})

    return jsonify({"timetable": data[sid].get("custom_timetable", [])})


# --- ASSIGNMENTS ---

@app.route("/api/assignments", methods=["POST"])
def add_assignment():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    assignment = {
        "name": request.json.get("name", ""),
        "subject": request.json.get("subject", ""),
        "marks": request.json.get("marks", 0),
        "total": request.json.get("total", 100),
        "status": "pending",
        "id": str(uuid.uuid4())[:6]
    }
    data[sid]["assignments"].append(assignment)
    save_all(data)
    return jsonify({"message": "Assignment added!", "assignment": assignment})


@app.route("/api/assignments-list")
def get_assignments():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"assignments": data[sid].get("assignments", [])})


@app.route("/api/assignments/status", methods=["PUT"])
def update_assignment_status():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    aid = request.json.get("assignment_id")
    status = request.json.get("status", "completed")
    for a in data[sid].get("assignments", []):
        if a.get("id") == aid:
            a["status"] = status
            save_all(data)
            return jsonify({"message": "Status updated!"})
    return jsonify({"error": "Assignment not found"}), 404


# --- EXAMS ---

@app.route("/api/exams", methods=["POST"])
def add_exam():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    is_college = s.get("student_type") == "college"
    exam_type = request.json.get("exam_type", "internal" if is_college else "quarterly")
    exam = {
        "name": request.json.get("name", ""),
        "subject": request.json.get("subject", ""),
        "marks": request.json.get("marks", 0),
        "total": request.json.get("total", 100),
        "exam_type": exam_type,
        "rank": request.json.get("rank", ""),
        "id": str(uuid.uuid4())[:6]
    }
    data[sid]["exams"].append(exam)
    save_all(data)
    return jsonify({"message": "Exam result added!", "exam": exam})


@app.route("/api/exams-list")
def get_exams():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({
        "exams": data[sid].get("exams", []),
        "is_college": data[sid].get("student_type") == "college"
    })


# --- SKILLS ---

@app.route("/api/careers-for-user")
def api_careers_for_user():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    careers = get_careers_for_student(s)
    return jsonify({"careers": careers})


@app.route("/api/skills-for-career")
def api_skills_for_career():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    career = s.get("selected_career", "")
    relevant_skills = get_skills_for_career(career)
    current_skills = s.get("skills", {})
    skill_details = []
    for sk in relevant_skills:
        info = SKILL_DATABASE.get(sk, {})
        skill_details.append({
            "key": sk, "name": sk.replace("_", " "),
            "domain": info.get("domain", ""),
            "current": current_skills.get(sk, 0)
        })
    return jsonify({
        "skills": skill_details, "career": career,
        "is_college": s.get("student_type") == "college"
    })


@app.route("/api/skills-data")
def api_skills_data():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    return jsonify({"skills": s.get("skills", {})})


@app.route("/api/skills", methods=["POST"])
def update_skills():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    skills = request.json.get("skills", {})
    data[sid]["skills"] = skills
    save_all(data)
    return jsonify({"message": "Skills updated!"})


# --- SKILL GAPS ---

@app.route("/api/skill-gaps")
def api_skill_gaps():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    is_college = s.get("student_type") == "college"
    career = request.args.get("career", s.get("selected_career", ""))
    skills = s.get("skills", {})
    gaps = analyze_skill_gaps(career, skills, is_college)
    recs = get_recommendations(career, skills, is_college)
    return jsonify({
        "selected_career": career, "gaps": gaps,
        "recommendations": recs, "is_college": is_college
    })


# --- DASHBOARD ---

@app.route("/api/dashboard")
def api_dashboard():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    is_college = s.get("student_type") == "college"

    att_data = {}
    for subj, recs in s.get("attendance", {}).items():
        if recs:
            att_data[subj] = round((sum(recs) / len(recs)) * 100, 1)
        else:
            att_data[subj] = 0.0
    overall_att = round(sum(att_data.values()) / len(att_data), 1) if att_data else 0.0

    att_warnings = []
    if is_college:
        for subj, pct in att_data.items():
            if pct < 75 and pct > 0:
                att_warnings.append({"subject": subj, "percentage": pct})

    all_assignments = s.get("assignments", [])
    completed = [a for a in all_assignments if a.get("status") == "completed"]
    pending = [a for a in all_assignments if a.get("status") != "completed"]
    avg_assign = 0.0
    if completed:
        avg_assign = round(sum(a["marks"] / a["total"] * 100 for a in completed) / len(completed), 1)

    exams = s.get("exams", [])
    avg_exam = 0.0
    if exams:
        avg_exam = round(sum(e["marks"] / e["total"] * 100 for e in exams) / len(exams), 1)

    cgpa = 0.0
    if is_college:
        scores = s.get("scores", {})
        if scores:
            cgpa = round(sum(scores.values()) / len(scores), 2)

    average_marks = 0.0
    if not is_college:
        scores = s.get("scores", {})
        if scores:
            average_marks = round(sum(scores.values()) / len(scores), 1)

    group_or_dept_name = ""
    rg = s.get("recommended_group", "")
    if is_college and rg in COLLEGE_DEPARTMENTS:
        group_or_dept_name = COLLEGE_DEPARTMENTS[rg]["name"]
    elif not is_college and rg in SCHOOL_GROUPS:
        group_or_dept_name = SCHOOL_GROUPS[rg]["name"]

    stats = {
        "cgpa": cgpa,
        "attendance": overall_att,
        "skills": len([v for v in s.get("skills", {}).values() if v > 0]),
        "exams": len(exams),
        "average_marks": average_marks,
        "subjects": len(s.get("scores", {}))
    }

    return jsonify({
        "name": s["name"], "grade": s.get("grade", ""),
        "is_college": is_college,
        "score_type": s.get("score_type", "marks"),
        "email": s.get("email", ""),
        "career_interest": s.get("career_interest", ""),
        "recommended_group": s.get("recommended_group", ""),
        "group_or_dept_name": group_or_dept_name,
        "selected_career": s.get("selected_career", ""),
        "scores": s.get("scores", {}),
        "attendance": att_data, "overall_attendance": overall_att,
        "att_warnings": att_warnings,
        "total_assignments": len(all_assignments),
        "completed_assignments": len(completed),
        "pending_assignments": len(pending),
        "avg_assignment_score": avg_assign,
        "total_exams": len(exams), "avg_exam_score": avg_exam,
        "skills": s.get("skills", {}), "cgpa": cgpa,
        "stats": stats
    })


# --- ROADMAP ---

@app.route("/api/roadmap")
def api_roadmap():
    data = load_all()
    sid = session.get("student_id")
    if not sid or sid not in data:
        return jsonify({"error": "Not logged in"}), 401
    s = data[sid]
    is_college = s.get("student_type") == "college"
    career = s.get("selected_career", "")
    gaps = analyze_skill_gaps(career, s.get("skills", {}), is_college)
    recs = get_recommendations(career, s.get("skills", {}), is_college)

    if is_college:
        short_term = [
            f"Master core subjects for {career}",
            "Complete industry-recognized certifications"
        ]
        for c in recs["courses"][:3]:
            short_term.append(f"Enroll in: {c}")
        for p in recs["practice"][:2]:
            short_term.append(f"Practice: {p}")

        medium_term = [
            f"Build real-world {career} projects"
        ]
        for p in recs["projects"][:3]:
            medium_term.append(f"Build: {p}")
        medium_term.append("Connect with industry professionals on LinkedIn")
        medium_term.append("Publish technical articles / case studies")

        long_term = [
            f"Apply for {career} internships",
            "Contribute to open-source projects",
            "Build a strong portfolio website",
            "Prepare for GATE / GRE / placements",
            "Attend tech conferences and hackathons",
            "Work on a major capstone project with real-world data"
        ]
    else:
        short_term = [
            f"Focus on building strong fundamentals for {career}",
            "Develop consistent study habits"
        ]
        if s.get("recommended_group") and s["recommended_group"] in SCHOOL_GROUPS:
            imp = get_subject_importance_school(s["recommended_group"], s.get("scores", {}))
            for item in imp[:3]:
                short_term.append(f"Study {item['subject']} (Importance: {item['importance']}%)")
        for c in recs["courses"][:2]:
            short_term.append(f"Learn basics: {c}")

        medium_term = [
            "Understand core concepts deeply",
            "Practice problems regularly"
        ]
        for p in recs["projects"][:2]:
            medium_term.append(f"Try simple project: {p}")
        for p in recs["practice"][:2]:
            medium_term.append(f"Practice: {p}")

        long_term = [
            f"Prepare for {career} related entrance exams",
            "Build a strong academic record",
            "Explore career through online courses",
            "Seek guidance from teachers and mentors",
            "Develop good study and time management skills",
            "Create a learning roadmap for higher education"
        ]

    return jsonify({
        "career": career, "is_college": is_college,
        "short_term": short_term, "medium_term": medium_term, "long_term": long_term
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)