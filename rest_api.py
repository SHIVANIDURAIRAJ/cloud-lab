import flask

app = flask.Flask(__name__)

students = [
    {"id": 1, "name": "Arun"},
    {"id": 2, "name": "Priya"}
]

@app.route('/students', methods=['GET'])
def get_students():
    return flask.jsonify(students)

@app.route('/students', methods=['POST'])
def add_student():
    data = flask.request.get_json()
    students.append(data)
    return flask.jsonify(data), 201


@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = flask.request.get_json()

    for student in students:
        if student['id'] == id:
            student['name'] = data['name']
            return flask.jsonify(student)

    return flask.jsonify({"message": "Student not found"}), 404


@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    global students
    students = [s for s in students if s['id'] != id]
    return flask.jsonify({"message": "Student deleted"})

if __name__ == '__main__':
    app.run(debug=True)
