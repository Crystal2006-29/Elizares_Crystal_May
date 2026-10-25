import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Classmate's deployed API
CLASSMATE_API = "https://palencia-shamainejoyce.onrender.com/students"


# Database connection
def get_db_connection():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Welcome API
@app.route("/api")
def welcome():
    return "Welcome to my first API!"


# Student information
@app.route("/student")
def get_student():
    return """Student Information
Student ID: 24-00379
Name: Crystal May Elizares
Program: BSIT
Year: 3
Section: B"""


# Hello API
@app.route("/hello")
def say_hello():
    name = request.args.get("name", "Student")
    return f"Hello, {name}! Welcome to the Student Management System."


# Course information
@app.route("/course")
def get_course():
    return """Course Information
Course Code: BSIT
Course Name: Bachelor of Science in Information Technology
Department: College of Computing Studies"""


# Get your own student records
@app.route("/students", methods=["GET"])
@app.route("/api/students", methods=["GET"])
def get_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id"
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# Add a student to your own database
@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Please provide student information in JSON format."
        }), 400

    required_fields = [
        "student_id", "name", "program", "year", "section"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            """INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)""",
            (
                data["student_id"],
                data["name"],
                data["program"],
                data["year"],
                data["section"]
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid
        }), 201

    except sqlite3.Error as error:
        conn.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        conn.close()


# Classmate's Records
@app.route("/api/classmate-records", methods=["GET"])
def get_classmate_records():
    try:
        response = requests.get(
            CLASSMATE_API,
            timeout=60,
            headers={"Accept": "application/json"}
        )

        response.raise_for_status()
        data = response.json()

        # Support common API response formats
        if isinstance(data, dict):
            for key in ("students", "records", "data"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break

        if not isinstance(data, list):
            return jsonify({
                "error": "The classmate API did not return a list of records.",
                "details": data
            }), 502

        return jsonify(data), 200

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "The classmate API took too long to respond."
        }), 504

    except requests.exceptions.RequestException as error:
        return jsonify({
            "error": "Unable to connect to the classmate API.",
            "details": str(error)
        }), 502

    except ValueError:
        return jsonify({
            "error": "The classmate API did not return valid JSON."
        }), 502


# Record Sources
@app.route("/api/record-sources", methods=["GET"])
def record_sources():
    return jsonify({
        "my_records": {
            "source": "My Flask API and SQLite database",
            "endpoint": "/api/students"
        },
        "classmate_records": {
            "source": "Classmate's deployed API",
            "endpoint": "/api/classmate-records",
            "original_api": CLASSMATE_API
        }
    })


# Database Independence
@app.route("/api/database-independence", methods=["GET"])
def database_independence():
    conn = get_db_connection()

    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        return jsonify({
            "status": "success",
            "local_database_reachable": True,
            "local_record_count": count,
            "local_database": "students.db",
            "classmate_database": "Separate external API",
            "independent": True,
            "message": (
                "Your student records are stored in your own database. "
                "Classmate records are fetched separately and are not "
                "added to or modified in your database."
            )
        })

    except sqlite3.Error as error:
        return jsonify({
            "status": "error",
            "local_database_reachable": False,
            "details": str(error)
        }), 500

    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)