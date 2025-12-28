from django.shortcuts import redirect, render,HttpResponse
from .models import Employee,Role,Department
from datetime import datetime
from django.contrib import messages
from django.db.models import Avg  
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
        
    return render(request, 'login.html')

@login_required(login_url='login')
def index(request):
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    total_roles = Role.objects.count()
    avg_salary = Employee.objects.aggregate(Avg('salary'))['salary__avg']

    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_roles': total_roles,
        'avg_salary': round(avg_salary or 0, 2),
    }
    return render(request, 'index.html', context)
    return render(request,'index.html')

@login_required(login_url='login')
def all_emp(request):
    emps = Employee.objects.all()
    context = {
        'emps':emps
    }
    return render(request,'all_emp.html',context)

@login_required(login_url='login')
def add_emp(request):
    if request.method == 'POST':
        try:
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            phone = int(request.POST['phone'])
            salary = int(request.POST['salary'])
            bonus = int(request.POST['bonus'])
            role = int(request.POST['role'])
            dept = int(request.POST['dept'])
            profile_pic = request.FILES.get('profile_pic')

            # basic validation
            if not first_name or not salary or not role or not dept:
                messages.error(request, "Please fill all required fields.")
                return redirect('add_emp')

            new_emp = Employee(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                salary=salary,
                bonus=bonus,
                role_id=role,
                dept_id=dept,
                hire_date=datetime.now(),
                profile_pic=profile_pic
            )
            new_emp.save()
            messages.success(request, "Employee added successfully.")
            return redirect('index')
        except Exception as e:
            messages.error(request, "An error occurred while adding the employee ")
            return redirect('add_emp')  
    
    elif request.method == 'GET':
        depts = Department.objects.all()
        roles = Role.objects.all()
        context = {
            'depts':depts,
            'roles':roles
        }
        return render(request,'add_emp.html',context)
    else:
        return HttpResponse("Invalid request")

@login_required(login_url='login')
def remove_emp(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        if emp_id:
            try:
                emp_to_be_removed = Employee.objects.get(id=emp_id)
                emp_to_be_removed.delete()
                messages.success(request, "Employee removed successfully.")
                return redirect('remove_emp')
            except Employee.DoesNotExist:
                messages.error(request, "Employee not found.")
                return redirect('remove_emp')
            except Exception:
                messages.error(request, "An error occurred while removing the employee.")
                return redirect('remove_emp')
    else:
        emps = Employee.objects.all()
        context = {
            'emps': emps
        }
        return render(request, 'remove_emp.html', context)

@login_required(login_url='login')
def filter_emp(request):
    emps = Employee.objects.all()
    depts = Department.objects.all()
    roles = Role.objects.all()

    if request.method == 'GET':
        name = request.GET.get('name')
        dept = request.GET.get('dept')
        role = request.GET.get('role')
        min_salary = request.GET.get('min_salary')
        max_salary = request.GET.get('max_salary')
        
        if name:
            emps = emps.filter(first_name__icontains = name) | emps.filter(last_name__icontains = name)

        if dept:
            emps = emps.filter(dept_id = dept)

        if role:
            emps = emps.filter(role_id=role)

        if min_salary:
            emps = emps.filter(salary__gte=min_salary)

        if max_salary:
            emps = emps.filter(salary__lte=max_salary)

        context = {
            'emps': emps,
            'depts': depts,
            'roles': roles
        }
        return render(request, 'filter_emp.html', context)
    
def admin_logout(request):
    logout(request)
    return redirect('login')

