from django.contrib import admin

# Local Django models
from .models import Note, Category

# Adding models to the Django admin dashboard
admin.site.register(Category)
admin.site.register(Note)
