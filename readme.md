# EduTrack - Course Management System

## Overview
EduTrack is a lightweight course management system that allows teachers to create courses and assignments, while students can enroll, view courses, and submit assignments.

## Features
- User roles: Teacher and Student
- Course management (create, update, delete, view)
- Assignment creation and submission
- Enrollment system
- Custom permissions for different user roles
- RESTful API with DRF
- API documentation with Swagger/OpenAPI

## Technologies
- Django 4.0
- Django REST Framework
- PostgreSQL
- Docker
- DRF Spectacular (OpenAPI 3.0 schema generation)

## Environment Configuration

Create a `.env` file with the following variables:

```ini
SECRET_KEY=Ijske9)jne@
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=edutrack_db
POSTGRES_USER=edutrack_user
POSTGRES_PASSWORD=postgrespw
POSTGRES_HOST=db
POSTGRES_PORT=5432

ENV_MODE=development
DOCKER_WEB_PORT=8000
DOCKER_DB_PORT=5432

SPECTACULAR_TITLE=EduTrack API
SPECTACULAR_DESCRIPTION=Course Management System
SPECTACULAR_VERSION=1.0.0

# Key Assumptions

## Users
- Strict teacher/student role separation
- No role switching after creation
- Teachers cannot enroll as students

## Courses
- Single teacher per course
- Teachers have full control over their courses
- Enrollment required for student access

## Assignments
- One submission per student per assignment
- Teachers manage all assignment lifecycle
- No late submissions allowed

## Submissions
- Immutable after submission
- Only teachers can view/grade submissions
- Review status tracked explicitly


**Setup Run the Application**  
1.clone the repo   using git clone 
2 . Use the following command to start the application:
  ```bash
  docker-compose up --build
  ```
3 for test run
docker-compose exec web pytest -vv
