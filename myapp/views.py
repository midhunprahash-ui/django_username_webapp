import pandas as pd
from thefuzz import fuzz
import jellyfish
import re
import io
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Employee, Department
from .forms import UsernameCSVUploadForm
from django.contrib.auth.decorators import login_required


SCORE_THRESHOLD = 50


def compute_match_score(username, employee_name, first_name, last_name, emp_id):
    username_lower = str(username).lower().strip()
    employee_name_lower = str(employee_name).lower().strip()
    first_name_lower = str(first_name).lower().strip()
    last_name_lower = str(last_name).lower().strip()
    emp_id_str = str(emp_id).lower().strip()

    username_parts = re.split(r'[\._\-\s]', username_lower)
    part1 = username_parts[0] if len(username_parts) > 0 else ''
    part2 = username_parts[1] if len(username_parts) > 1 else ''

    possible_patterns = [
        f"{first_name_lower}.{last_name_lower}",
        f"{last_name_lower}.{first_name_lower}",
        f"{first_name_lower}_{last_name_lower}",
        f"{last_name_lower}_{first_name_lower}",
        f"{first_name_lower}{last_name_lower}",
        f"{last_name_lower}{first_name_lower}",
        f"{first_name_lower} {last_name_lower}",
        f"{last_name_lower} {first_name_lower}"
    ]
    if username_lower in possible_patterns:
        return 100.0

    split_bonus = 0
    if ((part1 == first_name_lower and part2 == last_name_lower) or
        (part2 == first_name_lower and part1 == last_name_lower)):
        split_bonus += 10

    number_match_bonus = 0
    if emp_id_str and emp_id_str in username_lower:
        number_match_bonus += 5

    lev_full = fuzz.ratio(username_lower, employee_name_lower)
    partial_full = fuzz.partial_ratio(username_lower, employee_name_lower)
    token_set_full = fuzz.token_set_ratio(username_lower, employee_name_lower)

    token_set_first = fuzz.token_set_ratio(username_lower, first_name_lower)
    token_set_last = fuzz.token_set_ratio(username_lower, last_name_lower)

    soundex_match_last = int(jellyfish.soundex(username_lower) == jellyfish.soundex(last_name_lower))
    metaphone_match_last = int(jellyfish.metaphone(username_lower) == jellyfish.metaphone(last_name_lower))
    soundex_match_first = int(jellyfish.soundex(username_lower) == jellyfish.soundex(first_name_lower))
    metaphone_match_first = int(jellyfish.metaphone(username_lower) == jellyfish.metaphone(first_name_lower))

    initial_bonus = 0
    if username_lower and first_name_lower and username_lower[0] == first_name_lower[0]:
        initial_bonus += 5
    if '.' in username_lower:
        parts = username_lower.split('.')
        if len(parts) > 1 and first_name_lower and parts[1] and parts[1][0] == first_name_lower[0]:
            initial_bonus += 5

    composite = (
        (lev_full * 0.2) +
        (partial_full * 0.2) +
        (token_set_full * 0.2) +
        (token_set_last * 0.3) +
        (token_set_first * 0.2) +
        (soundex_match_last * 6) +
        (metaphone_match_last * 7) +
        (soundex_match_first * 3) +
        (metaphone_match_first * 3) +
        split_bonus +
        initial_bonus +
        number_match_bonus
    )
    return min(composite, 100)

@login_required
def unauthorized_employees(request):
    form = UsernameCSVUploadForm()
    unauthorized_employee_list = []

    if request.method == 'POST':
        form = UsernameCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            usernames_csv = request.FILES['usernames_csv_file']

            if not usernames_csv.name.endswith('.csv'):
                messages.error(request, 'Please upload a CSV file.')
                return render(request, 'myapp/unauthorized_employees.html', {
                    'form': form,
                    'unauthorized_employee_list': unauthorized_employee_list
                })

            try:
                usernames_data = usernames_csv.read().decode('utf-8')
                usernames_buffer = io.StringIO(usernames_data)
                usernames_df = pd.read_csv(usernames_buffer)
                usernames_df.columns = usernames_df.columns.str.lower()

                if 'username' not in usernames_df.columns:
                    messages.error(request, "Usernames CSV must contain a 'username' column.")
                    return render(request, 'myapp/unauthorized_employees.html', {
                        'form': form,
                        'unauthorized_employee_list': unauthorized_employee_list
                    })

                input_usernames = usernames_df['username'].astype(str).tolist()
            except Exception as e:
                messages.error(request, f"Error reading usernames CSV: {e}")
                return render(request, 'myapp/unauthorized_employees.html', {
                    'form': form,
                    'unauthorized_employee_list': unauthorized_employee_list
                })

            employees_from_db = Employee.objects.all()
            if not employees_from_db.exists():
                messages.warning(request, "No employee data found in the database. Please ensure employee data is loaded.")
                return render(request, 'myapp/unauthorized_employees.html', {
                    'form': form,
                    'unauthorized_employee_list': unauthorized_employee_list
                })

            for employee in employees_from_db:
                is_authorized = False
                employee_data_for_matching = {
                    'employee_name': employee.employee_name,
                    'first_name': employee.first_name,
                    'last_name': employee.last_name,
                    'emp_id': employee.emp_id
                }

                for username in input_usernames:
                    score = compute_match_score(
                        username,
                        employee_data_for_matching['employee_name'],
                        employee_data_for_matching['first_name'],
                        employee_data_for_matching['last_name'],
                        employee_data_for_matching['emp_id']
                    )
                    if score >= SCORE_THRESHOLD:
                        is_authorized = True
                        break

                if not is_authorized:
                    unauthorized_employee_list.append({
                        'emp_id': employee.emp_id,
                        'employee_name': employee.employee_name,
                        'email': employee.email if employee.email else 'N/A',
                        'department': employee.department.name if employee.department else 'N/A',
                        'job_title': employee.job_title if employee.job_title else 'N/A',
                    })
            
            messages.success(request, "Authorization check completed. See results below.")
            
    return render(request, 'myapp/unauthorized_employees.html', {
        'form': form,
        'unauthorized_employee_list': unauthorized_employee_list
    })


@login_required
def projects(request):
    context = {
        'page_title': 'My Projects',
        'message': 'This is the projects page. Content will go here!',
    }
    return render(request, 'myapp/projects.html', context)
