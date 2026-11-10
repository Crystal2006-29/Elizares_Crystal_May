
import sqlite3
import requests

from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DATABASE = "students.db"


# ==========================================
# CLASSMATE / PARTNER API
# ==========================================

CLASSMATE_API_URLS = [
    "https://palencia-shamainejoyce.onrender.com/students",
    "https://palencia-shamainejoyce.onrender.com/api/students"
]

PARTNER_POST_URL = (
    "https://palencia-shamainejoyce.onrender.com/api/students"
)


# ==========================================
# ORIGINAL STUDENT RECORDS
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
# ==========================================

def initialize_database():

    conn = get_db_connection()

    try:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                source TEXT DEFAULT 'Local'
            )
        """)

        # CHECK EXISTING COLUMNS

        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        ]

        # ADD SOURCE COLUMN TO OLD DATABASE

        if "source" not in columns:

            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        # SET EMPTY SOURCE TO LOCAL

        conn.execute("""
            UPDATE students
            SET source = 'Local'
            WHERE source IS NULL OR TRIM(source) = ''
        """)

        # INSERT ORIGINAL RECORDS ONLY IF DATABASE IS EMPTY

        count = conn.execute("""
            SELECT COUNT(*) FROM students
        """).fetchone()[0]

        if count == 0:

            conn.executemany("""
                INSERT INTO students
                (
                    student_id,
                    name,
                    program,
                    year,
                    section,
                    source
                )
                VALUES (?, ?, ?, ?, ?, 'Local')
            """, students)

        conn.commit()

    finally:
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

    name = request.args.get(
        "name",
        "Student"
    ).strip()

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

    for field in required_fields:

        if field not in data or str(data[field]).strip() == "":

            return jsonify({
                "error": f"{field} is required."
            }), 400

    try:

        student_id = str(data["student_id"]).strip()
        name = str(data["name"]).strip()
        program = str(data["program"]).strip()
        year = int(data["year"])
        section = str(data["section"]).strip()

        # LOCAL OR EXTERNAL SOURCE

        source = str(
            data.get("source", "Local")
        ).strip()

        if not source:
            source = "Local"

        if year < 1 or year > 4:

            return jsonify({
                "error": "Year must be between 1 and 4."
            }), 400

        conn = get_db_connection()

        try:

            # CHECK DUPLICATE STUDENT ID

            existing = conn.execute("""
                SELECT id FROM students
                WHERE student_id = ?
            """, (student_id,)).fetchone()

            if existing:

                return jsonify({
                    "error": "Student ID already exists."
                }), 409

            # CHECK DUPLICATE NAME

            existing_name = conn.execute("""
                SELECT id FROM students
                WHERE LOWER(TRIM(name)) = LOWER(TRIM(?))
            """, (name,)).fetchone()

            if existing_name:

                return jsonify({
                    "error": "Student name already exists."
                }), 409

            # INSERT STUDENT

            conn.execute("""
                INSERT INTO students
                (
                    student_id,
                    name,
                    program,
                    year,
                    section,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                name,
                program,
                year,
                section,
                source
            ))

            conn.commit()

            return jsonify({
                "message": "Student added successfully!",
                "source": source
            }), 201

        finally:
            conn.close()

    except (ValueError, TypeError):

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
# 6. VIEW ALL LOCAL STUDENTS
# ==========================================

@app.route("/students", methods=["GET"])
@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    try:

        records = conn.execute("""
            SELECT
                id,
                student_id,
                name,
                program,
                year,
                section,
                source
            FROM students
            ORDER BY id ASC
        """).fetchall()

        return jsonify([
            dict(row) for row in records
        ])

    finally:
        conn.close()


# ==========================================
# 7. GET ONE STUDENT
# ==========================================

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_one_student(student_id):

    conn = get_db_connection()

    try:

        record = conn.execute("""
            SELECT * FROM students
            WHERE id = ?
        """, (student_id,)).fetchone()

        if not record:

            return jsonify({
                "error": "Student record not found."
            }), 404

        return jsonify(dict(record))

    finally:
        conn.close()


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

    for value in updates.values():

        if value is None or str(value).strip() == "":

            return jsonify({
                "error": "Fields cannot be empty."
            }), 400

    try:

        for field in updates:

            if field != "year":
                updates[field] = str(
                    updates[field]
                ).strip()

        if "year" in updates:

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

            return jsonify({
                "error": "Student record not found."
            }), 404

        # CHECK DUPLICATE STUDENT ID

        if "student_id" in updates:

            duplicate = conn.execute("""
                SELECT id FROM students
                WHERE student_id = ? AND id != ?
            """, (
                updates["student_id"],
                student_id
            )).fetchone()

            if duplicate:

                return jsonify({
                    "error": "Student ID already exists."
                }), 409

        # CHECK DUPLICATE NAME

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

        return jsonify({
            "message": "Student record updated successfully!"
        })

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Student ID already exists."
        }), 409

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        conn.close()


# ==========================================
# 9. DELETE STUDENT
# ==========================================

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    conn = get_db_connection()

    try:

        cursor = conn.execute("""
            DELETE FROM students
            WHERE id = ?
        """, (student_id,))

        conn.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Student record not found."
            }), 404

        return jsonify({
            "message": "Student deleted successfully!"
        })

    finally:
        conn.close()


# ==========================================
# 10. FETCH PARTNER RECORDS
# ==========================================

def fetch_partner_records():

    last_error = "Partner API is unavailable."

    for url in CLASSMATE_API_URLS:

        try:

            response = requests.get(
                url,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            # PARTNER RETURNS A LIST

            if isinstance(data, list):

                records = data

            # PARTNER RETURNS A DICTIONARY

            elif isinstance(data, dict):

                records = (
                    data.get("students")
                    or data.get("records")
                    or data.get("data")
                )

            else:

                records = None

            if not isinstance(records, list):

                last_error = "Invalid student data from partner API."
                continue

            # RETURN PARTNER RECORDS

            return jsonify([
                {
                    **record,
                    "source": "Partner"
                }
                for record in records
                if isinstance(record, dict)
            ])

        except requests.RequestException as e:

            last_error = str(e)

        except ValueError:

            last_error = "Partner API returned invalid JSON."

    return jsonify({
        "error": "Unable to retrieve partner data.",
        "details": last_error
    }), 502


# ==========================================
# 11. DISPLAY CLASSMATE RECORDS
# ==========================================

@app.route("/api/classmate-records", methods=["GET"])
def classmate_records():

    return fetch_partner_records()


# ==========================================
# 12. DISPLAY PARTNER RECORDS
# ==========================================

@app.route("/partner-records", methods=["GET"])
def partner_records():

    return fetch_partner_records()


# ==========================================
# 13. IMPORT PARTNER STUDENT
# ==========================================

@app.route("/import-student", methods=["POST"])
def import_student():

    data = request.get_json(silent=True) or {}

    required_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    for field in required_fields:

        if field not in data or str(data[field]).strip() == "":

            return jsonify({
                "error": f"{field} is required."
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

        try:

            # CHECK IF ALREADY IMPORTED

            existing = conn.execute("""
                SELECT id FROM students
                WHERE student_id = ?
            """, (student_id,)).fetchone()

            if existing:

                return jsonify({
                    "error": "This student is already saved in your database."
                }), 409

            # SAVE PARTNER RECORD

            conn.execute("""
                INSERT INTO students
                (
                    student_id,
                    name,
                    program,
                    year,
                    section,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                name,
                program,
                year,
                section,
                "Classmate API"
            ))

            conn.commit()

            return jsonify({
                "message": "Remote record saved successfully!",
                "source": "Classmate API"
            }), 201

        finally:
            conn.close()

    except (ValueError, TypeError):

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
# 14. SEND PRACTICE RECORD TO PARTNER
# ==========================================

@app.route("/send-to-partner", methods=["POST"])
def send_to_partner():

    data = request.get_json(silent=True) or {}

    required_fields = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    for field in required_fields:

        if field not in data or str(data[field]).strip() == "":

            return jsonify({
                "error": f"{field} is required."
            }), 400

    try:

        year = int(data["year"])

        if year < 1 or year > 4:

            return jsonify({
                "error": "Year must be between 1 and 4."
            }), 400

        record = {
            "student_id": str(data["student_id"]).strip(),
            "name": str(data["name"]).strip(),
            "program": str(data["program"]).strip(),
            "year": year,
            "section": str(data["section"]).strip(),
            "source": "Partner API"
        }

        response = requests.post(
            PARTNER_POST_URL,
            json=record,
            timeout=20
        )

        try:
            partner_response = response.json()
        except ValueError:
            partner_response = response.text

        if not response.ok:

            return jsonify({
                "error": "Partner API rejected the record.",
                "partner_status": response.status_code,
                "partner_response": partner_response
            }), 502

        return jsonify({
            "message": "Student record sent successfully!",
            "partner_status": response.status_code,
            "partner_response": partner_response
        }), 200

    except requests.RequestException as e:

        return jsonify({
            "error": "Unable to connect to partner API.",
            "details": str(e)
        }), 502

    except (ValueError, TypeError):

        return jsonify({
            "error": "Invalid year level."
        }), 400


# ==========================================
# INITIALIZE DATABASE
# ==========================================

initialize_database()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
