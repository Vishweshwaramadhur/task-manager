# Task Manager Application

A simple web-based task manager built with Flask, HTML, CSS, and JavaScript.

## Implementation Approach

- Backend: Used Flask to create routes (URLs) for adding, toggling, and deleting tasks
- Frontend: Built with HTML, CSS, and JavaScript. JavaScript uses fetch() API to communicate with the backend
- Data Storage: Tasks are stored in a MySQL database. Data is fetched and updated directly from the database
- Error Handling: Added basic validation and error responses using Flask and jsonify

## Features

- Add new tasks with title and description
- Mark tasks as complete/incomplete
- Delete tasks
- View all tasks in a list
- Data saved in MySQL database

## Requirements

- Python 3.x (tested on Python 3.12.3)
- Flask
- MySQL Server
- mysql-connector-python

## Project Structure

task-manager/
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
├── README.md
└── .gitignore

## Installation & Setup

Step 1: Clone the repository

git clone <your-repo-url>

Step 2: Enter the project folder

cd task-manager

Step 3: Create and activate the virtual environment

python3 -m venv venv
source venv/bin/activate

Step 4: Install required packages

pip install flask mysql-connector-python

## Database Setup

sudo mysql

CREATE DATABASE taskmanager;
USE taskmanager;

CREATE TABLE tasks (
id INT AUTO_INCREMENT PRIMARY KEY,
title VARCHAR(100),
description TEXT,
completed BOOLEAN DEFAULT FALSE
);

## How to Run

1. Open terminal in project folder

2. Run the application

python3 app.py

3. Open your browser and go to

http://127.0.0.1:5000

4. Stop the server
- Press Ctrl + C in terminal
- Enter deactivate

## How to Use

1. Add Task: Enter title and description, click "Add Task"
2. Complete Task: Click the "Complete" button (or "Incomplete" to undo)
3. Delete Task: Click "Delete" button and confirm
