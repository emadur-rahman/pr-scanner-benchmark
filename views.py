from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

SECRET_KEY = "django-insecure-xK9mP2qR8vL3nJ5wT7yB4cF6hD1eG0"

def search_patients(request):
    name = request.GET.get("name")
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM patients WHERE name = '%s'" % name)
        rows = cursor.fetchall()
    return JsonResponse({"results": rows})
