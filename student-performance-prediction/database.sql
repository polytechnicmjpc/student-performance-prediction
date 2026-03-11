DROP DATABASE IF EXISTS student_prediction;
CREATE DATABASE student_prediction;
USE student_prediction;

-- ================= ACADEMIC LEVEL =================

CREATE TABLE academic_levels (
id INT AUTO_INCREMENT PRIMARY KEY,
level_name VARCHAR(100)
);

INSERT INTO academic_levels (level_name)
VALUES ('Polytechnic');


-- ================= COURSES =================

CREATE TABLE courses (
id INT AUTO_INCREMENT PRIMARY KEY,
course_name VARCHAR(100),
level_id INT,
FOREIGN KEY (level_id) REFERENCES academic_levels(id)
);

INSERT INTO courses (course_name, level_id) VALUES
('Mechanical Engineering',1),
('Civil Engineering',1),
('Electrical Engineering',1),
('Automobile Engineering',1),
('Computer Engineering',1);


-- ================= SUBJECTS =================

CREATE TABLE subjects (
id INT AUTO_INCREMENT PRIMARY KEY,
subject_name VARCHAR(150),
course_id INT,
FOREIGN KEY (course_id) REFERENCES courses(id)
);


-- ================= COMPUTER ENGINEERING SUBJECTS =================

INSERT INTO subjects (subject_name,course_id) VALUES
('Cloud Computing',5),
('Cyber Security',5),
('Machine Learning',5),
('Deep Learning',5),
('Data Science',5),
('Big Data Analytics',5),
('Internet of Things',5),
('Mobile App Development',5),
('Blockchain Technology',5),
('Distributed Systems',5),
('Computer Graphics',5),
('Natural Language Processing',5),
('Parallel Computing',5),
('DevOps Engineering',5),
('UI/UX Design',5),
('Software Testing',5),
('Game Development',5),
('Augmented Reality',5);


-- ================= MECHANICAL SUBJECTS =================

INSERT INTO subjects (subject_name,course_id) VALUES
('Engineering Materials',1),
('Strength of Materials',1),
('Machine Tools',1),
('Advanced Manufacturing',1),
('Tool Engineering',1),
('Robotics',1),
('Automation in Manufacturing',1),
('Maintenance Engineering',1),
('Quality Control',1),
('Project Management',1),
('Energy Engineering',1),
('Composite Materials',1),
('Finite Element Analysis',1),
('Mechatronics',1),
('Computer Integrated Manufacturing',1);


-- ================= CIVIL SUBJECTS =================

INSERT INTO subjects (subject_name,course_id) VALUES
('Advanced Structural Analysis',2),
('Foundation Engineering',2),
('Rock Mechanics',2),
('Bridge Engineering',2),
('Tunnel Engineering',2),
('Earthquake Engineering',2),
('Coastal Engineering',2),
('Urban Planning',2),
('Solid Waste Management',2),
('Remote Sensing and GIS',2);


-- ================= ELECTRICAL SUBJECTS =================

INSERT INTO subjects (subject_name,course_id) VALUES
('Embedded Systems',3),
('Industrial Drives',3),
('PLC and SCADA',3),
('Electric Vehicles',3),
('Smart Grid Technology',3),
('High Voltage Engineering',3),
('Energy Management',3),
('Electric Traction',3),
('Signal Processing',3),
('Communication Systems',3);


-- ================= AUTOMOBILE SUBJECTS =================

INSERT INTO subjects (subject_name,course_id) VALUES
('Internal Combustion Engines',4),
('Automobile Chassis Design',4),
('Automobile Fuel Systems',4),
('Automotive Safety',4),
('Automobile Aerodynamics',4),
('Vehicle Testing',4),
('Automobile Service Technology',4),
('Automobile Manufacturing',4),
('Electric Vehicles',4),
('Autonomous Vehicles',4);


-- ================= STUDENTS TABLE =================

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course VARCHAR(100) NOT NULL,
    avg_marks FLOAT NOT NULL,
    study_hours FLOAT NOT NULL,
    final_score FLOAT NOT NULL
);


INSERT INTO students (course, avg_marks, study_hours, final_score) VALUES
('Computer Engineering',60,2,65),
('Computer Engineering',70,3,75),
('Mechanical Engineering',55,2,60),
('Civil Engineering',50,1,55),
('Electrical Engineering',80,4,85);