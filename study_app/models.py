from django.db import models
from django.contrib.auth.models import User


class UploadedNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    uploaded_file = models.FileField(upload_to='notes/')
    extracted_text = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Summary(models.Model):
    uploaded_note = models.ForeignKey(
        UploadedNote,
        on_delete=models.CASCADE
    )
    ai_model = models.CharField(max_length=50)
    summary_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.uploaded_note.title} - {self.ai_model}"


class SavedSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    summary = models.ForeignKey(Summary, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.summary}"