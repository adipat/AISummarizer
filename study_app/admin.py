from django.contrib import admin
from .models import UploadedNote, Summary, SavedSummary


admin.site.register(UploadedNote)
admin.site.register(Summary)
admin.site.register(SavedSummary)