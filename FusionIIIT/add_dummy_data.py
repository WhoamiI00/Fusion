import os
import sys
import django
import datetime
import random

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fusion.settings.development")
django.setup()

# Import Django models
from django.contrib.auth.models import User
from django.utils import timezone
from applications.globals.models import ExtraInfo, DepartmentInfo, HoldsDesignation, Designation, Faculty
from applications.academic_information.models import Student, Course as AICourse, Curriculum
from applications.programme_curriculum.models import Course, Discipline, Programme, Curriculum as PCCurriculum, Semester, CourseSlot, CourseInstructor, Batch
from applications.central_mess.models import Feedback as MessFeedback, Menu, Monthly_bill
from applications.complaint_system.models import Caretaker, StudentComplain
from applications.health_center.models import Doctor, Complaint, All_Prescription as Prescription
from applications.online_cms.models import CourseDocuments, QuestionBank

# Create departments if they don't exist
departments = ['CSE', 'ECE', 'ME', 'DESIGN', 'CE', 'EE']
for dept_name in departments:
    try:
        dept = DepartmentInfo.objects.get(name=dept_name)
        print(f"{dept_name} department already exists")
    except DepartmentInfo.DoesNotExist:
        dept = DepartmentInfo.objects.create(name=dept_name)
        print(f"Created {dept_name} department")

# Create disciplines
disciplines = [
    {'name': 'Computer Science and Engineering', 'acronym': 'CSE'},
    {'name': 'Electronics and Communication Engineering', 'acronym': 'ECE'},
    {'name': 'Mechanical Engineering', 'acronym': 'ME'},
    {'name': 'Design', 'acronym': 'DES'},
    {'name': 'Civil Engineering', 'acronym': 'CE'},
    {'name': 'Electrical Engineering', 'acronym': 'EE'}
]

for disc in disciplines:
    try:
        discipline = Discipline.objects.get(name=disc['name'])
        print(f"{disc['name']} discipline already exists")
    except Discipline.DoesNotExist:
        discipline = Discipline.objects.create(name=disc['name'], acronym=disc['acronym'])
        print(f"Created {disc['name']} discipline")

# Create programmes
programmes = [
    {'name': 'Bachelor of Technology', 'category': 'UG'},
    {'name': 'Master of Technology', 'category': 'PG'},
    {'name': 'Doctor of Philosophy', 'category': 'PHD'}
]

for prog in programmes:
    try:
        programme = Programme.objects.get(name=prog['name'])
        print(f"{prog['name']} programme already exists")
    except Programme.DoesNotExist:
        programme = Programme.objects.create(name=prog['name'], category=prog['category'])
        print(f"Created {prog['name']} programme")

# Link disciplines to programmes
for discipline in Discipline.objects.all():
    for programme in Programme.objects.all():
        discipline.programmes.add(programme)
    discipline.save()
    print(f"Linked {discipline.name} to all programmes")

# Create courses
courses_data = [
    {
        'code': 'CS101',
        'name': 'Introduction to Computer Science',
        'credit': 4,
        'lecture_hours': 3,
        'tutorial_hours': 1,
        'pratical_hours': 2,
        'syllabus': 'Introduction to programming concepts, algorithms, and data structures.'
    },
    {
        'code': 'CS201',
        'name': 'Data Structures',
        'credit': 4,
        'lecture_hours': 3,
        'tutorial_hours': 1,
        'pratical_hours': 2,
        'syllabus': 'Advanced data structures and algorithms.'
    },
    {
        'code': 'CS301',
        'name': 'Database Systems',
        'credit': 4,
        'lecture_hours': 3,
        'tutorial_hours': 1,
        'pratical_hours': 2,
        'syllabus': 'Database design, SQL, and database management systems.'
    },
    {
        'code': 'EC101',
        'name': 'Basic Electronics',
        'credit': 4,
        'lecture_hours': 3,
        'tutorial_hours': 1,
        'pratical_hours': 2,
        'syllabus': 'Introduction to electronic circuits and components.'
    },
    {
        'code': 'ME101',
        'name': 'Engineering Mechanics',
        'credit': 4,
        'lecture_hours': 3,
        'tutorial_hours': 1,
        'pratical_hours': 2,
        'syllabus': 'Basic principles of mechanics for engineering applications.'
    },
]

for course_data in courses_data:
    try:
        course = Course.objects.get(code=course_data['code'])
        print(f"Course {course_data['code']} already exists")
    except Course.DoesNotExist:
        course = Course.objects.create(
            code=course_data['code'],
            name=course_data['name'],
            credit=course_data['credit'],
            lecture_hours=course_data['lecture_hours'],
            tutorial_hours=course_data['tutorial_hours'],
            pratical_hours=course_data['pratical_hours'],
            syllabus=course_data['syllabus'],
            ref_books="Reference books for " + course_data['name']
        )
        print(f"Created course {course_data['code']}")
        
        # Link course to appropriate discipline
        if course_data['code'].startswith('CS'):
            course.disciplines.add(Discipline.objects.get(acronym='CSE'))
        elif course_data['code'].startswith('EC'):
            course.disciplines.add(Discipline.objects.get(acronym='ECE'))
        elif course_data['code'].startswith('ME'):
            course.disciplines.add(Discipline.objects.get(acronym='ME'))

# Create AI Courses (for academic_information app)
for course_data in courses_data:
    try:
        ai_course = AICourse.objects.get(course_name=course_data['name'])
        print(f"AI Course {course_data['name']} already exists")
    except AICourse.DoesNotExist:
        ai_course = AICourse.objects.create(
            course_name=course_data['name'],
            course_details=course_data['syllabus']
        )
        print(f"Created AI Course {course_data['name']}")

# Create curriculum entries
for course in AICourse.objects.all():
    try:
        curriculum = Curriculum.objects.get(course_id=course, course_code=Course.objects.filter(name=course.course_name).first().code)
        print(f"Curriculum for {course.course_name} already exists")
    except Curriculum.DoesNotExist:
        curriculum = Curriculum.objects.create(
            course_code=Course.objects.filter(name=course.course_name).first().code,
            course_id=course,
            credits=4,
            course_type="Professional Core",
            programme="B.Tech",
            branch="CSE",
            batch=2020,
            sem=1,
            floated=True
        )
        print(f"Created curriculum for {course.course_name}")

# Create PC Curriculum
try:
    pc_curriculum = PCCurriculum.objects.get(name="BTech CSE Curriculum")
    print("PC Curriculum already exists")
except PCCurriculum.DoesNotExist:
    pc_curriculum = PCCurriculum.objects.create(
        name="BTech CSE Curriculum",
        programme=Programme.objects.get(name="Bachelor of Technology"),
        working_curriculum=True,
        no_of_semester=8,
        min_credit=160
    )
    print("Created PC Curriculum")

# Create semesters
for i in range(1, 9):
    try:
        semester = Semester.objects.get(curriculum=pc_curriculum, semester_no=i)
        print(f"Semester {i} already exists")
    except Semester.DoesNotExist:
        semester = Semester.objects.create(
            curriculum=pc_curriculum,
            semester_no=i,
            instigate_semester=True if i == 1 else False
        )
        print(f"Created semester {i}")

# Create course slots
slot_types = ["Professional Core", "Professional Elective", "Professional Lab", "Humanities"]
for semester in Semester.objects.all():
    for slot_type in slot_types:
        try:
            slot = CourseSlot.objects.get(semester=semester, name=f"{slot_type} {semester.semester_no}", type=slot_type)
            print(f"Course slot {slot_type} for semester {semester.semester_no} already exists")
        except CourseSlot.DoesNotExist:
            slot = CourseSlot.objects.create(
                semester=semester,
                name=f"{slot_type} {semester.semester_no}",
                type=slot_type
            )
            print(f"Created course slot {slot_type} for semester {semester.semester_no}")

# Add courses to slots
for slot in CourseSlot.objects.all():
    for course in Course.objects.all()[:2]:  # Add first two courses to each slot
        slot.courses.add(course)
    print(f"Added courses to slot {slot.name}")

# Create batch
try:
    batch = Batch.objects.get(name="B.Tech", discipline=Discipline.objects.get(acronym="CSE"), year=2020)
    print("Batch already exists")
except Batch.DoesNotExist:
    batch = Batch.objects.create(
        name="B.Tech",
        discipline=Discipline.objects.get(acronym="CSE"),
        year=2020,
        curriculum=pc_curriculum,
        running_batch=True
    )
    print("Created batch")

# Create more student users
student_data = [
    {
        'username': 'student1',
        'password': 'student123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'student1@example.com',
        'id': '2020002',
        'programme': 'B.Tech',
        'department': 'CSE',
        'hall_no': 1,
        'room_no': 'A-101'
    },
    {
        'username': 'student2',
        'password': 'student123',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'student2@example.com',
        'id': '2020003',
        'programme': 'B.Tech',
        'department': 'ECE',
        'hall_no': 2,
        'room_no': 'B-202'
    },
    {
        'username': 'student3',
        'password': 'student123',
        'first_name': 'Bob',
        'last_name': 'Johnson',
        'email': 'student3@example.com',
        'id': '2020004',
        'programme': 'B.Tech',
        'department': 'ME',
        'hall_no': 3,
        'room_no': 'C-303'
    },
]

for data in student_data:
    try:
        user = User.objects.get(username=data['username'])
        print(f"User {data['username']} already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        print(f"Created user {data['username']}")
    
    try:
        extra_info = ExtraInfo.objects.get(id=data['id'])
        print(f"ExtraInfo for {data['username']} already exists")
    except ExtraInfo.DoesNotExist:
        extra_info = ExtraInfo.objects.create(
            id=data['id'],
            user=user,
            title="Mr." if data['first_name'] in ['John', 'Bob'] else "Ms.",
            sex="M" if data['first_name'] in ['John', 'Bob'] else "F",
            date_of_birth=datetime.date(2000, 1, 1),
            address="Student Address",
            phone_no=9876543210,
            user_type="student",
            department=DepartmentInfo.objects.get(name=data['department'])
        )
        print(f"Created ExtraInfo for {data['username']}")
    
    try:
        student = Student.objects.get(id=extra_info)
        print(f"Student {data['username']} already exists")
    except Student.DoesNotExist:
        student = Student.objects.create(
            id=extra_info,
            programme=data['programme'],
            batch=2020,
            batch_id=Batch.objects.get(name="B.Tech", year=2020),
            cpi=random.uniform(7.0, 10.0),
            category="GEN",
            father_name=f"{data['first_name']}'s Father",
            mother_name=f"{data['first_name']}'s Mother",
            hall_no=data['hall_no'],
            room_no=data['room_no']
        )
        print(f"Created Student {data['username']}")

# Create more faculty users
faculty_data = [
    {
        'username': 'faculty1',
        'password': 'faculty123',
        'first_name': 'Professor',
        'last_name': 'Smith',
        'email': 'faculty1@example.com',
        'id': 'F002',
        'department': 'CSE'
    },
    {
        'username': 'faculty2',
        'password': 'faculty123',
        'first_name': 'Professor',
        'last_name': 'Johnson',
        'email': 'faculty2@example.com',
        'id': 'F003',
        'department': 'ECE'
    },
    {
        'username': 'faculty3',
        'password': 'faculty123',
        'first_name': 'Professor',
        'last_name': 'Williams',
        'email': 'faculty3@example.com',
        'id': 'F004',
        'department': 'ME'
    },
]

for data in faculty_data:
    try:
        user = User.objects.get(username=data['username'])
        print(f"User {data['username']} already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        print(f"Created user {data['username']}")
    
    try:
        extra_info = ExtraInfo.objects.get(id=data['id'])
        print(f"ExtraInfo for {data['username']} already exists")
    except ExtraInfo.DoesNotExist:
        extra_info = ExtraInfo.objects.create(
            id=data['id'],
            user=user,
            title="Dr.",
            sex="M",
            date_of_birth=datetime.date(1975, 1, 1),
            address="Faculty Address",
            phone_no=9876543210,
            user_type="faculty",
            department=DepartmentInfo.objects.get(name=data['department'])
        )
        print(f"Created ExtraInfo for {data['username']}")
    
    try:
        faculty = Faculty.objects.get(id=extra_info)
        print(f"Faculty {data['username']} already exists")
    except Faculty.DoesNotExist:
        faculty = Faculty.objects.create(
            id=extra_info
        )
        print(f"Created Faculty {data['username']}")

# Create course instructors
for course in Course.objects.all():
    for faculty in Faculty.objects.all()[:2]:  # Assign first two faculty to each course
        try:
            instructor = CourseInstructor.objects.get(course_id=course, instructor_id=faculty)
            print(f"Course instructor for {course.code} already exists")
        except CourseInstructor.DoesNotExist:
            instructor = CourseInstructor.objects.create(
                course_id=course,
                instructor_id=faculty,
                year=2023,
                semester_no=1
            )
            print(f"Created course instructor for {course.code}")

# Create health center data
# Add doctors
doctor_data = [
    {
        'name': 'Dr. John Smith',
        'phone': '9876543210',
        'specialization': 'General Physician'
    },
    {
        'name': 'Dr. Sarah Johnson',
        'phone': '9876543211',
        'specialization': 'Orthopedic Surgeon'
    }
]

for data in doctor_data:
    try:
        doctor = Doctor.objects.get(doctor_name=data['name'])
        print(f"Doctor {data['name']} already exists")
    except Doctor.DoesNotExist:
        doctor = Doctor.objects.create(
            doctor_name=data['name'],
            doctor_phone=data['phone'],
            specialization=data['specialization']
        )
        print(f"Created doctor {data['name']}")

# Create prescriptions instead of appointments
for student in Student.objects.all():
    for doctor in Doctor.objects.all():
        try:
            prescription = Prescription.objects.get(user_id=student.id.id, doctor_id=doctor)
            print(f"Prescription for {student.id.user.username} already exists")
        except Prescription.DoesNotExist:
            prescription = Prescription.objects.create(
                user_id=student.id.id,
                doctor_id=doctor,
                details="Regular checkup prescription",
                date=datetime.datetime.now().date(),
                suggestions="Take rest and drink plenty of water"
            )
            print(f"Created prescription for {student.id.user.username}")

# Create complaint system data
# Add caretakers
caretaker_data = [
    {
        'name': 'John Caretaker',
        'area': 'hall-1',
    },
    {
        'name': 'Jane Caretaker',
        'area': 'hall-3',
    }
]

# First create staff users for caretakers
for i, data in enumerate(caretaker_data):
    staff_username = f"caretaker{i+1}"
    try:
        user = User.objects.get(username=staff_username)
        print(f"User {staff_username} already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=staff_username,
            password="caretaker123",
            email=f"{staff_username}@example.com",
            first_name=data['name'].split()[0],
            last_name=data['name'].split()[1]
        )
        print(f"Created user {staff_username}")
    
    staff_id = f"CT00{i+1}"
    try:
        extra_info = ExtraInfo.objects.get(id=staff_id)
        print(f"ExtraInfo for {staff_username} already exists")
    except ExtraInfo.DoesNotExist:
        extra_info = ExtraInfo.objects.create(
            id=staff_id,
            user=user,
            title="Mr.",
            sex="M",
            date_of_birth=datetime.date(1980, 1, 1),
            address="Staff Address",
            phone_no=9876543220 + i,
            user_type="staff",
            department=DepartmentInfo.objects.get(name="CSE")
        )
        print(f"Created ExtraInfo for {staff_username}")
    
    try:
        caretaker = Caretaker.objects.get(staff_id=extra_info)
        print(f"Caretaker {data['name']} already exists")
    except Caretaker.DoesNotExist:
        caretaker = Caretaker.objects.create(
            staff_id=extra_info,
            area=data['area']
        )
        print(f"Created caretaker {data['name']}")

# Create student complaints
complaint_types = ['Electricity', 'carpenter', 'plumber', 'garbage']
for student in Student.objects.all():
    for complaint_type in complaint_types:
        try:
            complaint = StudentComplain.objects.get(complainer=student.id, complaint_type=complaint_type)
            print(f"{complaint_type} complaint for {student.id.user.username} already exists")
        except StudentComplain.DoesNotExist:
            complaint = StudentComplain.objects.create(
                complainer=student.id,
                complaint_type=complaint_type,
                location='hall-1' if student.hall_no == 1 else 'hall-3',
                specific_location=f"Room {student.room_no}",
                details=f"Issue with {complaint_type.lower()}",
                status=0,
                remarks="",
                complaint_date=timezone.now()
            )
            print(f"Created {complaint_type} complaint for {student.id.user.username}")

# Create central mess data
# Add menu items
menu_items = [
    {'meal_time': 'MB', 'dish': 'Bread, Butter, Jam, Milk'},
    {'meal_time': 'ML', 'dish': 'Rice, Dal, Vegetable Curry, Salad'},
    {'meal_time': 'MD', 'dish': 'Roti, Paneer, Rice, Dessert'},
    {'meal_time': 'TB', 'dish': 'Paratha, Curd, Pickle'},
    {'meal_time': 'TL', 'dish': 'Rice, Rajma, Vegetable, Salad'},
    {'meal_time': 'TD', 'dish': 'Roti, Chicken/Paneer, Rice, Ice Cream'}
]

for item in menu_items:
    try:
        menu = Menu.objects.get(meal_time=item['meal_time'])
        print(f"Menu for {item['meal_time']} already exists")
    except Menu.DoesNotExist:
        menu = Menu.objects.create(
            mess_option='mess1',
            meal_time=item['meal_time'],
            dish=item['dish']
        )
        print(f"Created menu for {item['meal_time']}")

# Create mess feedback
for student in Student.objects.all():
    try:
        feedback = MessFeedback.objects.get(student_id=student)
        print(f"Mess feedback for {student.id.user.username} already exists")
    except MessFeedback.DoesNotExist:
        feedback = MessFeedback.objects.create(
            student_id=student,
            fdate=timezone.now(),
            description="Food quality is good but can be improved.",
            feedback_type="maintenance"
        )
        print(f"Created mess feedback for {student.id.user.username}")

# Create monthly bills
for student in Student.objects.all():
    try:
        bill = Monthly_bill.objects.get(student_id=student)
        print(f"Monthly bill for {student.id.user.username} already exists")
    except Monthly_bill.DoesNotExist:
        bill = Monthly_bill.objects.create(
            student_id=student,
            month=timezone.now().month,
            year=timezone.now().year,
            amount=random.randint(2000, 3000),
            rebate_amount=random.randint(0, 500),
            total_bill=random.randint(1500, 2500)
        )
        print(f"Created monthly bill for {student.id.user.username}")

# Skipping online CMS data as the tables may not be migrated yet
# Uncomment and run after migrations are complete

# # Create online CMS data
# # Add course documents
# for course in Course.objects.all():
#     try:
#         doc = CourseDocuments.objects.get(course_id=course)
#         print(f"Course document for {course.code} already exists")
#     except CourseDocuments.DoesNotExist:
#         doc = CourseDocuments.objects.create(
#             course_id=course,
#             upload_time=timezone.now(),
#             description=f"Lecture notes for {course.name}",
#             document_title=f"{course.code} Lecture Notes"
#         )
#         print(f"Created course document for {course.code}")

# # Add question banks
# for course in Course.objects.all():
#     try:
#         qb = QuestionBank.objects.get(course_id=course, instructor_id=Faculty.objects.first())
#         print(f"Question bank for {course.code} already exists")
#     except QuestionBank.DoesNotExist:
#         qb = QuestionBank.objects.create(
#             course_id=course,
#             instructor_id=Faculty.objects.first(),
#             description=f"Sample questions for {course.name}",
#             quiz_title=f"{course.code} Quiz"
#         )
#         print(f"Created question bank for {course.code}")

# Skipping academic calendar events as the module doesn't exist
# Uncomment and modify if the module is added in the future

# # Create academic calendar events
# events = [
#     {'description': 'Semester Registration', 'from_date': timezone.now(), 'to_date': timezone.now() + timezone.timedelta(days=5)},
#     {'description': 'Mid-semester Examination', 'from_date': timezone.now() + timezone.timedelta(days=30), 'to_date': timezone.now() + timezone.timedelta(days=37)},
#     {'description': 'End-semester Examination', 'from_date': timezone.now() + timezone.timedelta(days=90), 'to_date': timezone.now() + timezone.timedelta(days=100)},
#     {'description': 'Holiday - Independence Day', 'from_date': timezone.now() + timezone.timedelta(days=15), 'to_date': timezone.now() + timezone.timedelta(days=15)},
#     {'description': 'Holiday - Republic Day', 'from_date': timezone.now() + timezone.timedelta(days=45), 'to_date': timezone.now() + timezone.timedelta(days=45)},
# ]

# Create hostel data
from applications.hostel_management.models import Hall

halls = [
    {'id': 1, 'hall_id': 'H1', 'hall_name': 'Hall 1'},
    {'id': 2, 'hall_id': 'H2', 'hall_name': 'Hall 2'},
    {'id': 3, 'hall_id': 'H3', 'hall_name': 'Hall 3'},
]

for hall_data in halls:
    try:
        hall = Hall.objects.get(id=hall_data['id'])
        print(f"Hall {hall_data['hall_name']} already exists")
    except Hall.DoesNotExist:
        hall = Hall.objects.create(
            id=hall_data['id'],
            hall_id=hall_data['hall_id'],
            hall_name=hall_data['hall_name']
        )
        print(f"Created hall {hall_data['hall_name']}")

# Skipping room creation as the model structure is different

# Skipping placement data as the tables may not be migrated yet
# Uncomment and run after migrations are complete

# # Create placement data
# from applications.placement_cell.models import PlacementRecord, NotifyStudent, PlacementStatus
# 
# # First create NotifyStudent entries
# companies = [
#     {'name': 'Google', 'placement_type': 'PLACEMENT', 'ctc': 25.00, 'description': 'Software Engineer'},
#     {'name': 'Microsoft', 'placement_type': 'PLACEMENT', 'ctc': 22.00, 'description': 'Software Development Engineer'},
#     {'name': 'Amazon', 'placement_type': 'PLACEMENT', 'ctc': 23.00, 'description': 'SDE-1'},
#     {'name': 'Goldman Sachs', 'placement_type': 'PBI', 'ctc': 10.00, 'description': 'Summer Analyst'},
#     {'name': 'JP Morgan', 'placement_type': 'PBI', 'ctc': 9.00, 'description': 'Technology Intern'},
# ]
# 
# for company in companies:
#     try:
#         notify = NotifyStudent.objects.get(company_name=company['name'], placement_type=company['placement_type'])
#         print(f"{company['placement_type']} notification for {company['name']} already exists")
#     except NotifyStudent.DoesNotExist:
#         notify = NotifyStudent.objects.create(
#             company_name=company['name'],
#             placement_type=company['placement_type'],
#             ctc=company['ctc'],
#             description=company['description']
#         )
#         print(f"Created {company['placement_type']} notification for {company['name']}")
# 
# # Create placement records
# for company in companies:
#     try:
#         record = PlacementRecord.objects.get(name=company['name'], placement_type=company['placement_type'])
#         print(f"{company['placement_type']} record for {company['name']} already exists")
#     except PlacementRecord.DoesNotExist:
#         record = PlacementRecord.objects.create(
#             name=company['name'],
#             placement_type=company['placement_type'],
#             ctc=company['ctc'],
#             year=timezone.now().year
#         )
#         print(f"Created {company['placement_type']} record for {company['name']}")
# 
# # Create placement status for students
# for student in Student.objects.all():
#     for notify in NotifyStudent.objects.all():
#         if random.choice([True, False]):
#             try:
#                 status = PlacementStatus.objects.get(unique_id=student.id, notify_id=notify)
#                 print(f"Placement status for {student.id.user.username} at {notify.company_name} already exists")
#             except PlacementStatus.DoesNotExist:
#                 status = PlacementStatus.objects.create(
#                     unique_id=student.id,
#                     notify_id=notify,
#                     invitation='ACCEPTED',
#                     placed='PLACED' if random.choice([True, False]) else 'NOT PLACED'
#                 )
#                 print(f"Created placement status for {student.id.user.username} at {notify.company_name}")

# Skipping library data as the module may not exist or tables may not be migrated yet
# Uncomment and run after migrations are complete

# # Create library data
# from applications.library.models import Book
# 
# books = [
#     {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'publisher': 'MIT Press', 'year': 2009, 'subject': 'Computer Science'},
#     {'title': 'Data Structures and Algorithms', 'author': 'Narasimha Karumanchi', 'publisher': 'CareerMonk', 'year': 2017, 'subject': 'Computer Science'},
#     {'title': 'Fundamentals of Database Systems', 'author': 'Ramez Elmasri', 'publisher': 'Pearson', 'year': 2015, 'subject': 'Computer Science'},
#     {'title': 'Engineering Mathematics', 'author': 'B.S. Grewal', 'publisher': 'Khanna Publishers', 'year': 2018, 'subject': 'Mathematics'},
#     {'title': 'Mechanics of Materials', 'author': 'R.C. Hibbeler', 'publisher': 'Pearson', 'year': 2016, 'subject': 'Mechanical Engineering'},
#     {'title': 'Principles of Electronic Materials and Devices', 'author': 'S.O. Kasap', 'publisher': 'McGraw-Hill', 'year': 2017, 'subject': 'Electronics'},
# ]
# 
# for book_data in books:
#     try:
#         book = Book.objects.get(title=book_data['title'], author=book_data['author'])
#         print(f"Book '{book_data['title']}' already exists")
#     except Book.DoesNotExist:
#         book = Book.objects.create(
#             title=book_data['title'],
#             author=book_data['author'],
#             publisher=book_data['publisher'],
#             year=book_data['year'],
#             subject=book_data['subject'],
#             available_copies=random.randint(1, 5)
#         )
#         print(f"Created book '{book_data['title']}'")

print("\nDummy data created successfully!")
print("\nLogin credentials:")
print("Admin: username=admin, password=admin123")
print("Student: username=student, password=student123")
print("Faculty: username=faculty, password=faculty123")
print("\nAdditional students:")
for data in student_data:
    print(f"{data['username']}: password={data['password']}")
print("\nAdditional faculty:")
for data in faculty_data:
    print(f"{data['username']}: password={data['password']}")