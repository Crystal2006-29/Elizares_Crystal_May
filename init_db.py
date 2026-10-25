import sqlite3

# Connect to the database
conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Create the students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL
)
''')

# Clear existing records to avoid duplicates when rerunning
cursor.execute('DELETE FROM students')

# Student records
students = [
    ('24-00379', 'Michaella Pedotim', 'BSIT', 4, 'B'),
    ('24-00283', 'Seth Claire Palec', 'BSIT', 3, 'B'),
    ('24-00301', 'Gella Gale', 'BSIT', 3, 'B'),
    ('26-00212', 'Iren Joy Daquita', 'BSIT', 1, 'C'),
    ('25-00012', 'Rachel Ann Lorca', 'BSIT', 2, 'B')
]

# Insert student records
cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

# Save changes
conn.commit()

# Display all student records
cursor.execute('SELECT * FROM students')
records = cursor.fetchall()

print('Students from Database:')
for student in records:
    print(student)

# Close database connection
conn.close()

print('\nDatabase created successfully!')