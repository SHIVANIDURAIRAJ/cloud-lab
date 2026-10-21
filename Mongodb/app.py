from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
from pymongo.errors import PyMongoError
import os

load_dotenv()

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("MONGO_URI is missing. Add your MongoDB Atlas connection string to .env")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
db = client["CloudLab"]
students = db["students"]


def serialize_student(student):
    student["_id"] = str(student["_id"])
    return student


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def get_students():
    try:
        records = [serialize_student(s) for s in students.find().sort("name", 1)]
        return jsonify(records), 200
    except PyMongoError:
        app.logger.exception("Could not read students")
        return jsonify({"error": "Could not connect to the database. Check your Atlas settings."}), 503


@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    department = str(data.get("department", "")).strip()
    year = str(data.get("year", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not department or not year:
        return jsonify({"error": "Name, department and year are required."}), 400

    student = {
        "name": name,
        "department": department,
        "year": year,
        "email": email
    }

    try:
        result = students.insert_one(student)
        return jsonify({
            "message": "Student added successfully.",
            "student": serialize_student(students.find_one({"_id": result.inserted_id}))
        }), 201
    except PyMongoError:
        app.logger.exception("Could not add student")
        return jsonify({"error": "Could not save the student. Check your Atlas connection."}), 503


@app.route("/api/students/<student_id>", methods=["PUT"])
def update_student(student_id):
    if not ObjectId.is_valid(student_id):
        return jsonify({"error": "Invalid student ID."}), 400

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    department = str(data.get("department", "")).strip()
    year = str(data.get("year", "")).strip()
    email = str(data.get("email", "")).strip()

    if not name or not department or not year:
        return jsonify({"error": "Name, department and year are required."}), 400

    try:
        result = students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {
                "name": name,
                "department": department,
                "year": year,
                "email": email
            }}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Student not found."}), 404
        updated = students.find_one({"_id": ObjectId(student_id)})
        return jsonify({"message": "Student updated successfully.", "student": serialize_student(updated)}), 200
    except PyMongoError:
        app.logger.exception("Could not update student")
        return jsonify({"error": "Could not update the student. Check your Atlas connection."}), 503


@app.route("/api/students/<student_id>", methods=["DELETE"])
def delete_student(student_id):
    if not ObjectId.is_valid(student_id):
        return jsonify({"error": "Invalid student ID."}), 400

    try:
        result = students.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Student not found."}), 404
        return jsonify({"message": "Student deleted successfully."}), 200
    except PyMongoError:
        app.logger.exception("Could not delete student")
        return jsonify({"error": "Could not delete the student. Check your Atlas connection."}), 503


if __name__ == "__main__":
    app.run(debug=True)
