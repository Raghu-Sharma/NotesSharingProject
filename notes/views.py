from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, logout, login
from datetime import date
from .models import Signup
from django.contrib import messages


def index(request):
    return render(request, 'index.html')


def download_notes(request):
    notes = Notes.objects.filter(status="Accept")
    for note in notes:
        signup = Signup.objects.get(user=note.user)
        note.uploaded_by_role = signup.role
    return render(request, 'download_notes.html', {'notes': notes})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


from django.contrib.auth.models import User

def userlogin(request):
    email_error = ""
    password_error = ""

    if request.method == 'POST':
        u = request.POST['emailid']
        p = request.POST['pwd']
        try:
            user = User.objects.get(username=u)
            if user.check_password(p):
                login(request, user)
                return redirect('profile')
            else:
                password_error = "Invalid password. Please try again."
        except User.DoesNotExist:
            email_error = "Invalid email. Please check your email and try again."

    d = {'email_error': email_error, 'password_error': password_error}
    return render(request, 'login.html', d)



def Logout(request):
    logout(request)
    return redirect('index')


def signup1(request):
    if request.method == 'POST':
        f = request.POST.get('firstname')
        l = request.POST.get('lastname')
        c = request.POST.get('contact')
        e = request.POST.get('emailid')
        p = request.POST.get('password')
        s = request.POST.get('semester')
        b = request.POST.get('branch')
        r = request.POST.get('role')
        try:
            user = User.objects.create_user(username=e, password=p, first_name=f, last_name=l)
            Signup.objects.create(user=user, contact=c, semester=s, branch=b, role=r)
            return render(request, 'signup.html', {'error': "no"})
        except Exception as e:
            error = str(e)
    return render(request, 'signup.html', {'error': ""})


def profile(request):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    user = User.objects.get(id=request.user.id)
    data = Signup.objects.get(user=user)
    d = {'data': data, 'user': user}
    return render(request, 'profile.html', d)


def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    user = User.objects.get(id=request.user.id)
    data = Signup.objects.get(user=user)
    error = False
    if request.method == 'POST':
        f = request.POST['firstname']
        l = request.POST['lastname']
        c = request.POST['contact']
        s = request.POST['semester']
        b = request.POST.get('branch')
        if not b:
            error = True
            messages.error(request, 'Please select a branch.')
        else:
            user.first_name = f
            user.last_name = l
            data.contact = c
            data.semester = s
            data.branch = b
            user.save()
            data.save()
            error = True
    d = {'data': data, 'user': user, 'error': error}
    return render(request, 'edit_profile.html', d)


def changepassword(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    if request.method == "POST":
        old_password = request.POST.get('old')
        new_password = request.POST.get('new')
        confirm_password = request.POST.get('confirm')
        if new_password == confirm_password:
            user = User.objects.get(username=request.user.username)
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                error = "no"
            else:
                error = "Incorrect old password"
        else:
            error = "New password and confirmation do not match"

    return render(request, 'changepassword.html', {'error': error})


def upload_notes(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    if request.method == 'POST':
        try:
            b = request.POST['branch']
            s = request.POST['subject']
            y = request.POST['semester']
            n = request.FILES['notesfile']
            f = request.POST['filetype']
            d = request.POST['description']
            u = User.objects.get(username=request.user.username)
            Notes.objects.create(user=u, uploadingdate=date.today(), branch=b, subject=s, semester=y,
                                 notesfile=n, filetype=f, description=d, status='pending')
            error = "no"
        except:
            error = "yes"
    user = User.objects.get(id=request.user.id)
    data = Signup.objects.get(user=user)
    d = {'error': error, 'data': data}
    return render(request, 'upload_notes.html', d)


def view_mynotes(request):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    user = User.objects.get(id=request.user.id)
    notes = Notes.objects.filter(user=user)
    data = Signup.objects.get(user=user)
    d = {'notes': notes, 'data': data}
    return render(request, 'view_mynotes.html', d)


def viewallnotes(request):
    user_signup = Signup.objects.get(user=request.user)
    notes = Notes.objects.filter(status="Accept")
    for note in notes:
        signup = Signup.objects.get(user=note.user)
        note.uploaded_by_role = signup.role
    return render(request, 'viewallnotes.html', {'notes': notes})


def delete_mynotes(request, pid):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    notes = Notes.objects.filter(id=pid)
    notes.delete()
    return redirect('view_mynotes')


def login_teacher(request):
    error = ""
    if request.method == 'POST':
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "no"
            else:
                error = "yes"
        except:
            error = "yes"
    d = {'error': error}
    return render(request, 'login_teacher.html', d)


def teacher_home(request):
    if not request.user.is_staff:
        return redirect('login_teacher')

    pn = Notes.objects.filter(status="pending").count()
    an = Notes.objects.filter(status="Accept").count()
    rn = Notes.objects.filter(status="Reject").count()
    alln = Notes.objects.all().count()

    d = {'pn': pn, 'an': an, 'rn': rn, 'alln': alln}
    return render(request, 'teacher_home.html', d)


def view_users(request):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    users = Signup.objects.all()
    d = {'users': users}
    return render(request, 'view_users.html', d)


def delete_users(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    user = User.objects.get(id=pid)
    user.delete()
    return redirect('view_users')


def pending_notes(request):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    notes = Notes.objects.filter(status="pending")
    d = {'notes': notes}
    return render(request, 'pending_notes.html', d)


def accepted_notes(request):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    notes = Notes.objects.filter(status="Accept")
    d = {'notes': notes}
    return render(request, 'accepted_notes.html', d)


def rejected_notes(request):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    notes = Notes.objects.filter(status="Reject")
    d = {'notes': notes}
    return render(request, 'rejected_notes.html', d)


def all_notes(request):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    notes = Notes.objects.all()
    d = {'notes': notes}
    return render(request, 'all_notes.html', d)


def assign_status(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_teacher')
    notes = Notes.objects.get(id=pid)
    error = ""
    if request.method == 'POST':
        try:
            s = request.POST['status']
            notes.status = s
            notes.save()
            error = "no"
        except:
            error = "yes"
    d = {'notes': notes, 'error': error}
    return render(request, 'assign_status.html', d)


def delete_notes(request, pid):
    if not request.user.is_authenticated:
        return redirect('userlogin')
    notes = Notes.objects.filter(id=pid)
    notes.delete()
    return redirect('all_notes')
