from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to my first API!"


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00379",
        "name": "Crystal May Elizares",
        "program": "BSIT",
        "year": 3,
        "section": "B"
    })
@app.route('/course')
def get_course():
    return jsonify({
        "course": "IT3120",
        "program": "BSIT",
    })

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })
@app.route('/tala')
def say_tala():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Gwapa si, {name}!"
    })


if __name__ == '__main__':
    app.run(debug=True)
