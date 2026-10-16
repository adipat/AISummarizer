from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import os
import pdfplumber
from docx import Document
from django.conf import settings
from .models import UploadedNote, Summary,SavedSummary
from google import genai
from dotenv import load_dotenv
from openai import OpenAI
from django.http import HttpResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.urls import path
from django.contrib.auth import views as auth_views

load_dotenv()

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    except Exception:
        return None


def home(request):
    return render(request, 'home.html')


def register(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        # -------------------------
        # Username validation
        # -------------------------

        if len(username) < 3:
            messages.error(
                request,
                "Username must be at least 3 characters long."
            )
            return redirect("register")

        if len(username) > 30:
            messages.error(
                request,
                "Username cannot be more than 30 characters."
            )
            return redirect("register")

        if not re.match(r"^[A-Za-z0-9_]+$", username):
            messages.error(
                request,
                "Username can contain only letters, numbers and underscore."
            )
            return redirect("register")

        if User.objects.filter(username__iexact=username).exists():
            messages.error(
                request,
                "Username already exists."
            )
            return redirect("register")

        # -------------------------
        # Email validation
        # -------------------------

        try:
            validate_email(email)
        except ValidationError:
            messages.error(
                request,
                "Please enter a valid email address."
            )
            return redirect("register")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return redirect("register")

        # -------------------------
        # Password validation
        # -------------------------

        if len(password) < 8:
            messages.error(
                request,
                "Password must be at least 8 characters long."
            )
            return redirect("register")

        if not re.search(r"[A-Z]", password):
            messages.error(
                request,
                "Password must contain at least one uppercase letter."
            )
            return redirect("register")

        if not re.search(r"[a-z]", password):
            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )
            return redirect("register")

        if not re.search(r"[0-9]", password):
            messages.error(
                request,
                "Password must contain at least one number."
            )
            return redirect("register")

        if not re.search(r"[^A-Za-z0-9]", password):
            messages.error(
                request,
                "Password must contain at least one special character."
            )
            return redirect("register")

        if password != confirm_password:
            messages.error(
                request,
                "Passwords do not match."
            )
            return redirect("register")

        # -------------------------
        # Create user
        # -------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Registration successful. Please login."
        )

        return redirect("login")

    return render(request, "register.html")


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email:
            messages.error(
                request,
                "Please enter both your username and registered email address."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        try:
            user = User.objects.get(
                username__iexact=username,
                email__iexact=email
            )
        except User.DoesNotExist:
            messages.error(
                request,
                "No account was found with that username and email combination."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if len(new_password) < 8:
            messages.error(
                request,
                "Password must be at least 8 characters long."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if not re.search(r"[A-Z]", new_password):
            messages.error(
                request,
                "Password must contain at least one uppercase letter."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if not re.search(r"[a-z]", new_password):
            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if not re.search(r"[0-9]", new_password):
            messages.error(
                request,
                "Password must contain at least one number."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if not re.search(r"[^A-Za-z0-9]", new_password):
            messages.error(
                request,
                "Password must contain at least one special character."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if new_password != confirm_password:
            messages.error(
                request,
                "New passwords do not match."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        if user.check_password(new_password):
            messages.error(
                request,
                "New password must be different from your current password."
            )
            return render(
                request,
                "forgot_password.html",
                {"username": username, "email": email}
            )

        user.set_password(new_password)
        user.save()

        messages.success(
            request,
            "Your password has been reset successfully! Please login with your new password."
        )
        return redirect("login")

    return render(request, "forgot_password.html")


@login_required
def dashboard(request):

    notes = UploadedNote.objects.filter(
        user=request.user
    )

    search_query = request.GET.get("search", "")
    file_type = request.GET.get("file_type", "")
    sort = request.GET.get("sort", "newest")

    # Search by note title
    if search_query:
        notes = notes.filter(
            title__icontains=search_query
        )

    # Filter by file type
    if file_type:
        notes = notes.filter(
            uploaded_file__iendswith=file_type
        )

    # Sort notes
    if sort == "oldest":
        notes = notes.order_by("uploaded_at")
    else:
        notes = notes.order_by("-uploaded_at")

    saved_summaries = SavedSummary.objects.filter(
        user=request.user
    )

    context = {
        "notes": notes,
        "saved_summaries": saved_summaries,
        "notes_count": UploadedNote.objects.filter(
            user=request.user
        ).count(),
        "saved_count": saved_summaries.count(),
        "search_query": search_query,
        "file_type": file_type,
        "sort": sort,
    }

    return render(
        request,
        "dashboard.html",
        context
    )

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def upload_notes(request):

    if request.method == 'POST':

        title = request.POST['title']
        uploaded_file = request.FILES.get('uploaded_file')

        if not uploaded_file:
            messages.error(request, 'Please select a file.')
            return redirect('upload_notes')

        file_extension = os.path.splitext(
            uploaded_file.name
        )[1].lower()

        extracted_text = ""

        # PDF
        if file_extension == '.pdf':

            with pdfplumber.open(uploaded_file) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:
                        extracted_text += text + "\n"

        # DOCX
        elif file_extension == '.docx':

            document = Document(uploaded_file)

            for paragraph in document.paragraphs:

                extracted_text += paragraph.text + "\n"

        # TXT
        elif file_extension == '.txt':

            extracted_text = uploaded_file.read().decode(
                'utf-8'
            )

        else:

            messages.error(
                request,
                'Only PDF, DOCX and TXT files are allowed.'
            )

            return redirect('upload_notes')

        # Save to database

        UploadedNote.objects.create(
            user=request.user,
            title=title,
            uploaded_file=uploaded_file,
            extracted_text=extracted_text
        )

        messages.success(
            request,
            'Note uploaded and text extracted successfully.'
        )

        return redirect('dashboard')

    return render(request, 'upload_notes.html')

@login_required
def generate_gemini_summary(request, note_id):

    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    length = request.GET.get("length", "medium")

    length_instruction = {
        "short": "Keep the summary very short and include only the most important points.",
        "medium": "Create a balanced summary covering the important concepts.",
        "detailed": "Create a detailed summary covering the important concepts, explanations, and key points."
    }

    gemini_client = get_gemini_client()
    if not gemini_client:
        messages.error(
            request,
            "Gemini API key is not configured. Please add GEMINI_API_KEY to your .env file."
        )
        return redirect("dashboard")

    try:

        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
Create a study summary from these notes.

Summary length:
{length_instruction.get(length, length_instruction["medium"])}

Rules:
1. Use simple English.
2. Use clear headings.
3. Use bullet points where needed.
4. Do NOT use Markdown symbols like #, **, or tables.
5. Keep the summary neat and student-friendly.

Notes:
{note.extracted_text}
"""
        )

        summary = Summary.objects.create(
            uploaded_note=note,
            ai_model="Gemini",
            summary_text=response.text
        )

        return render(
            request,
            "ai_summary.html",
            {
                "note": note,
                "summary": summary,
                "length": length
            }
        )

    except Exception as e:

        print("GEMINI ERROR:", e)

        messages.error(
            request,
            "Gemini is temporarily unavailable. Please try again."
        )

        return redirect("dashboard")
@login_required
def save_summary(request, summary_id):

    summary = Summary.objects.get(
        id=summary_id,
        uploaded_note__user=request.user
    )

    if request.method == "POST":

        SavedSummary.objects.get_or_create(
            user=request.user,
            summary=summary
        )

        messages.success(
            request,
            "Summary saved successfully!"
        )

        return redirect("saved_summaries")

    return redirect("dashboard")
@login_required
def saved_summaries(request):
    saved = SavedSummary.objects.filter(
        user=request.user
    ).select_related("summary", "summary__uploaded_note")

    return render(
        request,
        "saved_summaries.html",
        {"saved_summaries": saved}
    )
@login_required
def generate_openai_summary(request, note_id):
    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    current_groq_client = get_groq_client()
    if not current_groq_client:
        messages.error(
            request,
            "Groq/OpenAI API key is not configured. Please add GROQ_API_KEY to your .env file."
        )
        return redirect("dashboard")

    try:
        response = current_groq_client.responses.create(
            model="openai/gpt-oss-20b",
            input=f"""
Create a concise study summary from these notes.

Rules:
1. Use simple English.
2. Use clear headings.
3. Use bullet points where needed.
4. Do NOT use Markdown symbols like #, **, or tables.
5. Keep the summary neat and student-friendly.

Notes:
{note.extracted_text}
"""
        )

        summary = Summary.objects.create(
            uploaded_note=note,
            ai_model="OpenAI",
            summary_text=response.output_text
        )

        return render(
            request,
            "ai_summary.html",
            {
                "note": note,
                "summary": summary
            }
        )

    except Exception as e:
        print("OPENAI ERROR:", e)

        messages.error(
            request,
            "OpenAI is temporarily unavailable. Please try again."
        )

        return redirect("dashboard")

@login_required
def compare_summaries(request, note_id):

    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    gemini_summary = Summary.objects.filter(
        uploaded_note=note,
        ai_model="Gemini"
    ).order_by("-generated_at").first()

    openai_summary = Summary.objects.filter(
        uploaded_note=note,
        ai_model="OpenAI"
    ).order_by("-generated_at").first()

    return render(
        request,
        "compare_summaries.html",
        {
            "note": note,
            "gemini_summary": gemini_summary,
            "openai_summary": openai_summary,
        }
    )

@login_required
def download_summary(request, summary_id):

    summary = Summary.objects.get(
        id=summary_id,
        uploaded_note__user=request.user
    )

    response = HttpResponse(
        summary.summary_text,
        content_type="text/plain"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{summary.uploaded_note.title}_summary.txt"'
    )

    return response

    
@login_required
def delete_saved_summary(request, saved_id):
    saved_summary = SavedSummary.objects.get(
        id=saved_id,
        user=request.user
    )

    if request.method == "POST":
        saved_summary.delete()
        messages.success(
            request,
            "Saved summary deleted successfully!"
        )

    return redirect("saved_summaries")

@login_required
def profile(request):

    uploaded_notes_count = UploadedNote.objects.filter(
        user=request.user
    ).count()

    saved_summaries_count = SavedSummary.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        "profile.html",
        {
            "uploaded_notes_count": uploaded_notes_count,
            "saved_summaries_count": saved_summaries_count,
        }
    )
@login_required
def edit_profile(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()

        # Username length
        if len(username) < 3:

            messages.error(
                request,
                "Username must be at least 3 characters long."
            )

            return render(request, "edit_profile.html", {"username": username, "email": email})

        if len(username) > 30:

            messages.error(
                request,
                "Username cannot be more than 30 characters."
            )

            return render(request, "edit_profile.html", {"username": username, "email": email})

        # Username characters
        if not re.match(r"^[A-Za-z0-9_]+$", username):
            messages.error(
                request,
                "Username can contain only letters, numbers and underscore."
            )
            return render(request, "edit_profile.html", {"username": username, "email": email})

        # Check duplicate username
        if User.objects.filter(
            username__iexact=username
        ).exclude(
            id=request.user.id
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(request, "edit_profile.html", {"username": username, "email": email})

        # Validate email
        try:

            validate_email(email)

        except ValidationError:

            messages.error(
                request,
                "Please enter a valid email address."
            )

            return render(request, "edit_profile.html", {"username": username, "email": email})

        # Check duplicate email
        if User.objects.filter(
            email__iexact=email
        ).exclude(
            id=request.user.id
        ).exists():

            messages.error(
                request,
                "This email is already registered."
            )

            return render(request, "edit_profile.html", {"username": username, "email": email})

        request.user.username = username
        request.user.email = email

        request.user.save()

        messages.success(
            request,
            "Profile updated successfully!"
        )

        return redirect("profile")

    return render(
        request,
        "edit_profile.html",
        {
            "username": request.user.username,
            "email": request.user.email
        }
    )
@login_required
def change_password(request):

    if request.method == "POST":

        old_password = request.POST.get("old_password", "")
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")


        # -------------------------
        # Check current password
        # -------------------------

        if not request.user.check_password(old_password):

            messages.error(
                request,
                "Current password is incorrect."
            )

            return redirect("change_password")


        # -------------------------
        # Check new password length
        # -------------------------

        if len(new_password) < 8:

            messages.error(
                request,
                "Password must be at least 8 characters long."
            )

            return redirect("change_password")


        # -------------------------
        # Check uppercase letter
        # -------------------------

        if not re.search(r"[A-Z]", new_password):

            messages.error(
                request,
                "Password must contain at least one uppercase letter."
            )

            return redirect("change_password")


        # -------------------------
        # Check lowercase letter
        # -------------------------

        if not re.search(r"[a-z]", new_password):

            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )

            return redirect("change_password")


        # -------------------------
        # Check number
        # -------------------------

        if not re.search(r"[0-9]", new_password):

            messages.error(
                request,
                "Password must contain at least one number."
            )

            return redirect("change_password")


        # -------------------------
        # Check special character
        # -------------------------

        if not re.search(r"[^A-Za-z0-9]", new_password):

            messages.error(
                request,
                "Password must contain at least one special character."
            )

            return redirect("change_password")


        # -------------------------
        # Check password confirmation
        # -------------------------

        if new_password != confirm_password:

            messages.error(
                request,
                "New passwords do not match."
            )

            return redirect("change_password")


        # -------------------------
        # Prevent same old password
        # -------------------------

        if request.user.check_password(new_password):

            messages.error(
                request,
                "New password must be different from your current password."
            )

            return redirect("change_password")


        # -------------------------
        # Set new password
        # -------------------------

        request.user.set_password(new_password)

        request.user.save()


        # Keep user logged in
        update_session_auth_hash(
            request,
            request.user
        )


        messages.success(
            request,
            "Password changed successfully!"
        )


        return redirect("profile")


    return render(
        request,
        "change_password.html"
    )


@login_required
def view_note(request, note_id):
    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    return render(
        request,
        "view_note.html",
        {"note": note}
    )

@login_required
def download_note(request, note_id):
    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    response = HttpResponse(
        note.uploaded_file.open("rb"),
        content_type="application/octet-stream"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{note.uploaded_file.name.split("/")[-1]}"'
    )

    return response
@login_required
def delete_note(request, note_id):
    note = UploadedNote.objects.get(
        id=note_id,
        user=request.user
    )

    if request.method == "POST":
        note.delete()

        messages.success(
            request,
            "Note deleted successfully!"
        )

        return redirect("dashboard")

    return redirect("dashboard")

