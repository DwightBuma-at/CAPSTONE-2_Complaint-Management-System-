from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def user_page(request):
    return render(request, 'user.html')

def index_alias(request):
    return render(request, 'index.html')

def admin(request):
    return render(request, 'admin.html')    

def admin_complaints(request):
    return render(request, 'admin-complaints.html')

def admin_users(request):
    return render(request, 'admin-users.html')