from django.shortcuts import render
from .models import Students, StudentDetails, Province, TownCity
from django.db.models import Count

def dashboard(request):
    # Limit to first 100 students to improve loading speed
    students = Students.objects.all()[:10]
    student_data = []

    for student in students:
        try:
            details = StudentDetails.objects.get(student=student)
            province = details.province.name if details.province else 'N/A'
            town = details.town_city.name if details.town_city else 'N/A'
        except StudentDetails.DoesNotExist:
            details = None
            province = 'N/A'
            town = 'N/A'

        student_data.append({
            'student_number': student.student_number,
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'gender': student.gender,
            'birthday': student.birthday,
            'contact_number': details.contact_number if details else 'N/A',
            'street': details.street if details else 'N/A',
            'town_city': town,
            'province': province,
            'zip_code': details.zip_code if details else 'N/A',
        })

    # Add total student count and gender breakdown (counts over full table)
    total_students = Students.objects.count()
    total_male = Students.objects.filter(gender=1).count()   # Assuming 1 = Male
    total_female = Students.objects.filter(gender=2).count() # Assuming 2 = Female

    # Aggregate students by province via StudentDetails
    province_counts = (
        StudentDetails.objects
        .values('province__id', 'province__name')
        .annotate(student_count=Count('student'))
    )
    
    provinces_data = []
    for item in province_counts:
        provinces_data.append({
            'code': getattr(item['province__id'], 'code', 'N/A'),  # Adjust if you have a code field in Province
            'name': item['province__name'] or 'Unknown',
            'student_count': item['student_count'],
            'change_percent': 5.2,  # example static value
        })

    pending_documents = [
        {'name': 'Drug Test', 'note': 'Students who have not submitted drug tests', 'pending_count': 10, 'icon_url': '/static/img/icons/documents/drug-test.png'},
        {'name': 'Clearance', 'note': 'Clearance forms yet to be submitted', 'pending_count': 15, 'icon_url': '/static/img/icons/documents/clearance.png'},
        {'name': 'Orientation Slip', 'note': 'Pending orientation slips', 'pending_count': 8, 'icon_url': '/static/img/icons/documents/orientation.png'},
        {'name': 'Copy of Grades', 'note': 'Students missing grade copies', 'pending_count': 12, 'icon_url': '/static/img/icons/documents/grades.png'},
        {'name': 'Enrollment Form', 'note': 'Enrollment forms not yet submitted', 'pending_count': 5, 'icon_url': '/static/img/icons/documents/enrollment.png'},
    ]
# Create metrics dictionary to match your template keys
    metrics = {
        'total_students': total_students,
        'male_count': total_male,
        'female_count': total_female,
        'province_count': len(provinces_data),
    }
    context = {
        'students': student_data,
        'provinces_data': provinces_data,
        'total_students': total_students,
        'total_male': total_male,
        'total_female': total_female,
        'metrics': metrics,
        'pending_documents': pending_documents,
    }

    return render(request, 'dashboard/index.html', context)
