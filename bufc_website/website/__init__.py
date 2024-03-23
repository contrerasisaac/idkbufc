import os
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.static_folder = 'static'  # Configure Flask to serve static files from the 'static' directory

class Student:
    def __init__(self, name):
        self.name = name
        self.points = 0  # Changed from votes to points

# Function to get list of image names from 'Screenshots' folder
def get_image_names():
    image_names = []
    screenshots_dir = os.path.join(app.static_folder, 'Screenshots')  # Update path to use os.path.join
    for filename in os.listdir(screenshots_dir):
        if filename.endswith('.png'):
            image_names.append(filename)
    return image_names

# Function to initialize students (images) with their names
def initialize_students():
    image_names = get_image_names()
    students = [Student(os.path.splitext(name)[0]) for name in image_names]
    return students

# Function to shuffle students list
def shuffle_students(students):
    random.shuffle(students)

# Initialize students
students = initialize_students()

# Leaderboard
leaderboard = []

# Function to update leaderboard
def update_leaderboard():
    global students
    voted_students = [student for student in students if student.points > 0]
    leaderboard = sorted(voted_students, key=lambda x: x.points, reverse=True)[:10]  # Sort and get top 10 voted students
    return leaderboard

# Function to get a random student excluding a specific student
def get_random_student_excluding(exclude_student):
    global students
    remaining_students = [student for student in students if student.name != exclude_student.name]
    return random.choice(remaining_students)

# Route for home page
@app.route('/')
def index():
    global students
    global leaderboard
    global voted_student  # Define voted_student globally
    
    shuffle_students(students)
    
    # Ensure at least two students are available
    if len(students) < 2:
        return "Insufficient students available for voting."
    
    # Initialize voted_student if not defined or if it's not in the list of students
    if 'voted_student' not in globals() or voted_student not in students:
        voted_student = random.choice(students)
    
    non_voted_student = get_random_student_excluding(voted_student)
    leaderboard = update_leaderboard()
    
    # Ensure non-voted student is initialized
    if non_voted_student is None:
        return "Error: Unable to initialize non-voted student."

    return render_template('index.html', student1=voted_student, student2=non_voted_student, leaderboard=leaderboard)

# Route for submitting vote
@app.route('/vote', methods=['POST'])
def vote():
    global voted_student
    global students

    voted_student_name = request.form['student']
    voted_student = next(student for student in students if student.name == voted_student_name)
    voted_student.points += 1  # Increment points

    # Reset both students to switch out with another pair
    voted_student = None
    non_voted_student = None

    return redirect(url_for('index'))


# Route for leaderboard
@app.route('/leaderboard')
def show_leaderboard():
    global leaderboard
    leaderboard = update_leaderboard()  # Update leaderboard before showing
    return render_template('leaderboard.html', leaderboard=leaderboard)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    app.run(debug=True)
