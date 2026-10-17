from fastapi import APIRouter, Path, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Optional
import json
from pathlib import Path

router = APIRouter(prefix = "/api/v1", tags=["students"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "students.json"

# Initial seed data used only when the JSON file doesn't exist yet
initial_students = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "age": 17,
        "level": 3
    }
]

def ensure_data_file():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(initial_students, f, indent=2)

def load_students():
    ensure_data_file()
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_students(students_list):
    ensure_data_file()
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(students_list, f, indent=2)

# Schemas

class Student(BaseModel):
    first_name: str
    last_name: str
    age: int
    level: int = Field(..., ge=0, lt=5)

class UpdateStudent(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    level: Optional[int] = Field(default=None , ge=0, lt=5)

# Routers

@router.get("/students")
def get_students():
    return load_students()

@router.get("/students/{student_id}")
def get_student(student_id: int):
    students = load_students()
    for student in students:
        if student.get("id") == student_id:
            return student
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Student with id {student_id} Not Found.")
@router.get("/student")
def get_student_by_name(first_name: Optional[str] = None):
    students = load_students()
    if first_name:
        results = [s for s in students if first_name.lower() in s["first_name"].lower()]
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No student(s) found matching the name '{first_name}'"
            )
        return results
    return students

@router.post("/students/", status_code=status.HTTP_201_CREATED)
def create_student(student: Student):
    students = load_students()
    prev_student = students[-1]
    new_student_id = prev_student["id"] + 1
    new_student = {
        "id": new_student_id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "age": student.age,
        "level": student.level,
    }
    students.append(new_student)
    save_students(students)
    return new_student

@router.put("/students/{student_id}")
def update_student(student_id: int, student: UpdateStudent):
    students = load_students()
    for existing_student in students:
        if existing_student["id"] == student_id:
            if student.first_name is not None:
                existing_student["first_name"] = student.first_name
            if student.last_name is not None:
                existing_student["last_name"] = student.last_name
            if student.age is not None:
                existing_student["age"] = student.age
            if student.level is not None:
                existing_student["level"] = student.level
            save_students(students)
            return existing_student

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Student Not Found.")

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    students = load_students()
    for index, student in enumerate(students):
        if student["id"] == student_id:
            students.pop(index)
            save_students(students)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Student Not Found.")