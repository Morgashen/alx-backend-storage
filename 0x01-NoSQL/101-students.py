#!/usr/bin/env python3
"""
Returns all students sorted by average score.
"""

from pymongo import MongoClient
import sys

def top_students(mongo_collection):
    """
    Retrieves all students from the specified MongoDB collection,
    calculates their average score, and returns the sorted list.

    Args:
        mongo_collection (pymongo.collection.Collection): The MongoDB collection object.

    Returns:
        list: A list of dictionaries, where each dictionary represents a student
             with the 'averageScore' key added.
    """
    students = list(mongo_collection.find())
    for student in students:
        total_score = sum(student["scores"])
        student["averageScore"] = total_score / len(student["scores"])
    return sorted(students, key=lambda x: x["averageScore"], reverse=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 top_students.py <database_name>")
        sys.exit(1)

    database_name = sys.argv[1]
    client = MongoClient()
    db = client[database_name]
    students_collection = db.students

    top_students_list = top_students(students_collection)
    for student in top_students_list:
        print(student)
