"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///project-tracker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a GitHub account name, print info about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM students
        WHERE github = :github
        """

    db_cursor = db.session.execute(QUERY, {'github': github})

    if is_invalid_student(github):
        print('Invalid student, please try again')
        return

    row = db_cursor.fetchone()

    print(f"Student: {row[0]} {row[1]}\nGitHub account: {row[2]}")



def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """
    INSERT INTO students (first_name, last_name, github)
    VALUES (:first_name, :last_name, :github)
    """
    db.session.execute(QUERY, {
        'first_name': first_name,
        'last_name': last_name,
        'github':github
    })

    db.session.commit()

    print(f"Successfully added student:{first_name} {last_name}")


def get_project_by_title(title):
    """Given a project title, print information about the project."""

    QUERY = """
    SELECT description,max_grade 
    FROM projects
    WHERE title = :title
    """

    if is_invalid_project_title(title):
        print('Invalid project title, please try again')
        return

    db_cursor = db.session.execute(QUERY, {'title':title})

    row = db_cursor.fetchone()

    print(f"Project: {title}\nDescription: {row[0]}\nMax grade: {row[1]}")


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """
        SELECT first_name, last_name, grade
        FROM grades
        JOIN students ON (grades.student_github = students.github)
        WHERE github = :github 
        AND project_title = :title
    """

    if is_invalid_student(github):
        print('Invalid student, please try again')
        return
    elif is_invalid_project_title(title):
        print('Invalid project title, please try again')
        return

    db_cursor = db.session.execute(QUERY, {'github': github, 'title': title})

    row = db_cursor.fetchone()

    print(f'Student: {row[0]} {row[1]}\nProject: {title}\nGrade: {row[2]}')

def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    
    QUERY = """
    INSERT INTO grades (student_github, project_title, grade)
    VALUES (:github, :title, :grade)
    """

    db.session.execute(QUERY, {'github': github, 'title': title, 'grade': grade})

    db.session.commit()

    print(f"Successfully added a grade of {grade} for {github}'s {title} project")

def add_project(title, description, max_grade):
    """Add a new project and print confirmation.

    Given a title, description, and max grade, add project to the
    database and print a confirmation message."""

    QUERY = """
        INSERT INTO projects (title, description, max_grade)
        VALUES (:title, :description, :max_grade)
    """

    db.session.execute(QUERY, {'title': title, 'description': description, 'max_grade': max_grade})

    db.session.commit()

    print(f'Successfully added {title} to the projects database')

def get_all_grades(github):
    """Given a student's github, print all grades for that student (one line per project/grade)."""

    QUERY = """
        SELECT first_name, last_name, project_title, grade, max_grade
        FROM grades
        JOIN students ON (grades.student_github = students.github)
        JOIN projects ON (grades.project_title = projects.title)
        WHERE student_github = :github
    """

    if is_invalid_student(github):
        print('Invalid student, please try again')
        return

    db_cursor = db.session.execute(QUERY, {'github': github})

    row = db_cursor.fetchone()
    print(f'All grades for {row[0]} {row[1]:}')

    while row is not None:
        print(f'{row[2]} Project: {row[3]}/{row[4]}')
        row = db_cursor.fetchone()

def is_invalid_student(github):
    """Returns True if a student is NOT in the database (ie if the student is invalid)"""

    QUERY = """
        SELECT *
        FROM students
        WHERE github = :github
    """

    db_cursor = db.session.execute(QUERY, {'github': github})

    return db_cursor.fetchone() == None

def is_invalid_project_title(title):
    """Returns True if a project is NOT in the database (ie if the project title is invalid)"""

    QUERY = """
        SELECT *
        FROM projects
        WHERE title = :title
    """

    db_cursor = db.session.execute(QUERY, {'title': title})

    return db_cursor.fetchone() == None

def is_valid_number_of_args(args, num):
    """Returns True if the number of args passed equals the number expected"""

    return len(args) == num

def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received
    as a command.
    """

    command = None

    while command != "quit":
        input_string = input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            if is_valid_number_of_args(args, 1):
                github = args[0]
                get_student_by_github(github)
            else:
                print("The 'students' command takes exactly one argument. Please try again.")

        elif command == "new_student":
            first_name, last_name, github = args  # unpack!
            make_new_student(first_name, last_name, github)
        
        elif command == "project_info":
            if is_valid_number_of_args(args, 1):
                title = args[0]
                get_project_by_title(title)
            else:
                print("The 'project_info' command takes exactly one argument. Please try again.")

        elif command == "get_grade":
            if is_valid_number_of_args(args, 2):
                github, title = args
                get_grade_by_github_title(github, title)
            else:
                print("The 'get_grade' command takes exactly two arguments. Please try again.")

        elif command == "assign_grade":
            if is_valid_number_of_args(args, 3):
                github, title, grade = args
                assign_grade(github, title, grade)
            else:
                print("The 'assign_grade' command takes exactly three arguments. Please try again.")

        elif command == "add_project":
            title, *description_list, max_grade_str = args
            max_grade = int(max_grade_str)
            description = ' '.join(description_list)
            add_project(title, description, max_grade)

        elif command == "get_all_grades":
            if is_valid_number_of_args(args, 1):
                github = args[0]
                get_all_grades(github)
            else:
                print("The 'get_all_grades' command takes exactly one argument. Please try again.")

        else:
            if command != "quit":
                print("Invalid Entry. Try again.")


if __name__ == "__main__":
    connect_to_db(app)

    handle_input()

    # To be tidy, we close our database connection -- though,
    # since this is where our program ends, we'd quit anyway.

    db.session.close()
