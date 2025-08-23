from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

# Create FastAPI instance
app = FastAPI(
    title="Student API",
    description="A simple student management API with HTML templates",
    version="1.0.0"
)

# -------------------------------
# Templates setup
# -------------------------------
templates = Jinja2Templates(directory="templates")

# -------------------------------
# Pydantic model for Student
# -------------------------------
class Student(BaseModel):
    id: int
    name: str
    age: int
    grade: str

# -------------------------------
# In-memory database
# -------------------------------
students_db = []
current_id = 0

# -------------------------------
# CRUD Endpoints (JSON API)
# -------------------------------

@app.post("/students/", response_model=Student)
async def create_student(student: Student):
    global current_id
    current_id += 1
    student.id = current_id
    students_db.append(student)
    return student

@app.get("/students/", response_model=List[Student])
async def read_all_students():
    return students_db

@app.get("/students/{student_id}", response_model=Student)
async def read_student(student_id: int):
    for student in students_db:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, updated_student: Student):
    for index, student in enumerate(students_db):
        if student.id == student_id:
            updated_student.id = student_id
            students_db[index] = updated_student
            return updated_student
    raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
async def delete_student(student_id: int):
    for index, student in enumerate(students_db):
        if student.id == student_id:
            del students_db[index]
            return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail="Student not found")

# -------------------------------
# HTML Template Routes
# -------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/students/html", response_class=HTMLResponse)
async def show_students(request: Request):
    return templates.TemplateResponse("students.html", {"request": request, "students": students_db})

@app.get("/students/html/{student_id}", response_class=HTMLResponse)
async def show_student_detail(request: Request, student_id: int):
    for student in students_db:
        if student.id == student_id:
            return templates.TemplateResponse("student_detail.html", {"request": request, "student": student})
    raise HTTPException(status_code=404, detail="Student not found")
