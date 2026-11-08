
import sqlite3
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

DATABASE = "students.db"

# ==========================================
# CLASSMATE'S DEPLOYED API
# ==========================================

CLASSMATE_API_URLS = [
    "https://palencia-shamainejoyce.onrender.com/students",
    "https://palencia-shamainejoyce.onrender.com/api/students"
]

# ==========================================
# ORIGINAL 5 STUDENT RECORDS
# ==========================================

students = [
    ('24-00379', 'Michaella Pedotim', 'BSIT', 4, 'B'),
    ('24-00283', 'Seth Claire Palec', 'BSIT', 3, 'B'),
    ('24-00301', 'Gella Gale', 'BSIT', 3, 'B'),
    ('26-00212', 'Iren Joy Daquita', 'BSIT', 1, 'C'),
    ('25-00012', 'Rachel Ann Lorca', 'BSIT', 2, 'B')
]


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================================
# INITIALIZE DATABASE
# INSERT 5 RECORDS ONLY IF EMPTY
# ==========================================

def initialize_database():

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            program TEXT NOT NULL,
            year INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    if count == 0:

        conn.executemany("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, students)

    conn.commit()
    conn.close()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# 1. API
# ==========================================

@app.route("/api")
def api():

    return jsonify({
        "message": "Welcome to my first API!",
        "status": "Success"
    })


# ==========================================
# 2. STUDENT INFORMATION
# ==========================================

@app.route("/student")
def student():

    return jsonify({
        "student_information": "Student Information",
        "student_id": "24-00379",
        "name": "Crystal May Elizares",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })


# ==========================================
# 3. HELLO
# ==========================================

@app.route("/hello")
def hello():

    name = request.args.get("name", "Student").strip()

    if not name:
        name = "Student"

    return jsonify({
        "message": f"Hello, {name}! Welcome to the Student Management System."
    })


# ==========================================
# 4. COURSE INFORMATION
# ==========================================

@app.route("/course")
def course():

    return jsonify({
        "course": "Bachelor of Science in Information Technology",
        "abbreviation": "BSIT",
        "year_levels": 4,
        "description": "Information Technology"
    })


# ==========================================
# 5. ADD STUDENT
# ==========================================

@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json(silent=True) or {}

    required_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    if any(
        field not in data or str(data[field]).strip() == ""
        for field in required_fields
    ):
        return jsonify({
            "error": "All fields are required."
        }), 400

    try:

        student_id = str(data["student_id"]).strip()
        name = str(data["name"]).strip()
        program = str(data["program"]).strip()
        year = int(data["year"])
        section = str(data["section"]).strip()

        if year < 1 or year > 4:
            return jsonify({
                "error": "Year must be between 1 and 4."
            }), 400

        conn = get_db_connection()

        duplicate_id = conn.execute("""
            SELECT id FROM students
            WHERE student_id = ?
        """, (student_id,)).fetchone()

        if duplicate_id:
            conn.close()
            return jsonify({
                "error": "Student ID already exists."
            }), 409

        duplicate_name = conn.execute("""
            SELECT id FROM students
            WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
        """, (name,)).fetchone()

        if duplicate_name:
            conn.close()
            return jsonify({
                "error": "Student name already exists."
            }), 409

        conn.execute("""
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            name,
            program,
            year,
            section
        ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student added successfully!"
        }), 201

    except ValueError:

        return jsonify({
            "error": "Invalid year level."
        }), 400

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# 6. VIEW ALL STUDENTS
# ==========================================

@app.route("/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    records = conn.execute("""
        SELECT * FROM students
        ORDER BY id
    """).fetchall()

    conn.close()

    return jsonify([
        {
            **dict(row),
            "source": "Local"
        }
        for row in records
    ])


# ==========================================
# 7. GET ONE STUDENT
# ==========================================

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_one_student(student_id):

    conn = get_db_connection()

    record = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    if not record:
        return jsonify({
            "error": "Student record not found."
        }), 404

    return jsonify(dict(record))


# ==========================================
# 8. UPDATE STUDENT
# ==========================================

@app.route("/api/students/<int:student_id>", methods=["PATCH"])
def update_student(student_id):

    data = request.get_json(silent=True) or {}

    allowed_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    updates = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }

    if not updates:
        return jsonify({
            "error": "No valid information provided."
        }), 400

    if any(
        value is None or str(value).strip() == ""
        for value in updates.values()
    ):
        return jsonify({
            "error": "Fields cannot be empty."
        }), 400

    for field in updates:
        if field != "year":
            updates[field] = str(updates[field]).strip()

    if "year" in updates:

        try:
            updates["year"] = int(updates["year"])

            if updates["year"] < 1 or updates["year"] > 4:
                return jsonify({
                    "error": "Year must be between 1 and 4."
                }), 400

        except (ValueError, TypeError):
            return jsonify({
                "error": "Invalid year level."
            }), 400

    conn = get_db_connection()

    try:

        existing = conn.execute("""
            SELECT id FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()

        if not existing:
            conn.close()
            return jsonify({
                "error": "Student record not found."
            }), 404

        if "student_id" in updates:

            duplicate_id = conn.execute("""
                SELECT id FROM students
                WHERE student_id = ? AND id != ?
            """, (
                updates["student_id"],
                student_id
            )).fetchone()

            if duplicate_id:
                conn.close()
                return jsonify({
                    "error": "Student ID already exists."
                }), 409

        if "name" in updates:

            duplicate_name = conn.execute("""
                SELECT id FROM students
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
                AND id != ?
            """, (
                updates["name"],
                student_id
            )).fetchone()

            if duplicate_name:
                conn.close()
                return jsonify({
                    "error": "Student name already exists."
                }), 409

        set_clause = ", ".join(
            f"{field} = ?" for field in updates
        )

        values = list(updates.values())
        values.append(student_id)

        conn.execute(
            f"UPDATE students SET {set_clause} WHERE id = ?",
            values
        )

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Student record updated successfully!"
        })

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except Exception as e:

        conn.close()

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# 9. DELETE STUDENT
# ==========================================

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    conn = get_db_connection()

    cursor = conn.execute("""
        DELETE FROM students
        WHERE id = ?
    """, (student_id,))

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    if deleted == 0:
        return jsonify({
            "error": "Student record not found."
        }), 404

    return jsonify({
        "message": "Student deleted successfully!"
    })


# ==========================================
# 10. CLASSMATE'S RECORDS
# ==========================================

@app.route("/api/classmate-records")
def classmate_records():

    last_error = "Classmate API is unavailable."

    for url in CLASSMATE_API_URLS:

        try:

            response = requests.get(
                url,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                records = data

            elif isinstance(data, dict):
                records = (
                    data.get("students")
                    or data.get("records")
                    or data.get("data")
                )

            else:
                records = None

            if not isinstance(records, list):
                last_error = "Invalid student data from classmate API."
                continue

            return jsonify([
                {
                    **record,
                    "source": "Classmate"
                }
                for record in records
                if isinstance(record, dict)
            ])

        except requests.RequestException as e:
            last_error = str(e)

        except ValueError:
            last_error = "Classmate API returned invalid JSON."

    return jsonify({
        "error": "Unable to connect to classmate's API.",
        "details": last_error
    }), 502


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    initialize_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )