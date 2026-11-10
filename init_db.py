import sqlite3

# ==========================================
# DATABASE CONNECTION
# ==========================================

conn = sqlite3.connect('students.db')
cursor = conn.cursor()


# ==========================================
# CREATE STUDENTS TABLE
# ==========================================

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')


# ==========================================
# CLEAR EXISTING RECORDS
# ==========================================

cursor.execute('DELETE FROM students')


# ==========================================
# STUDENT RECORDS
# ==========================================

students = [
    ('24-00379', 'Michaella Pedotim', 'BSIT', 4, 'B', 'Local'),
    ('24-00283', 'Seth Claire Palec', 'BSIT', 3, 'B', 'Local'),
    ('24-00301', 'Gella Gale', 'BSIT', 3, 'B', 'Local'),
    ('26-00212', 'Iren Joy Daquita', 'BSIT', 1, 'C', 'Local'),
    ('25-00012', 'Rachel Ann Lorca', 'BSIT', 2, 'B', 'Local')
]


# ==========================================
# INSERT STUDENT RECORDS
# ==========================================

cursor.executemany('''
INSERT INTO students (
    student_id,
    name,
    program,
    year,
    section,
    source
)
VALUES (?, ?, ?, ?, ?, ?)
''', students)


# ==========================================
# SAVE CHANGES
# ==========================================

conn.commit()


# ==========================================
# DISPLAY ALL STUDENT RECORDS
# ==========================================

cursor.execute('SELECT * FROM students')
records = cursor.fetchall()

print('\n======================================')
print('       STUDENTS FROM DATABASE')
print('======================================')

for student in records:
    print('ID:', student[0])
    print('Student ID:', student[1])
    print('Name:', student[2])
    print('Program:', student[3])
    print('Year:', student[4])
    print('Section:', student[5])
    print('Source:', student[6])
    print('--------------------------------------')


# ==========================================
# CLOSE DATABASE CONNECTION
# ==========================================

conn.close()

print('\nDatabase created successfully!')
print('Source field added successfully!')
print('All student records have been saved as Local.')