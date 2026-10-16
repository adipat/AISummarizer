from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),

    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload_notes, name='upload_notes'),
    path(
    'generate-gemini/<int:note_id>/',
    views.generate_gemini_summary,
    name='generate_gemini_summary'
),
path(
    'save-summary/<int:summary_id>/',
    views.save_summary,
    name='save_summary'
),
path(
    'saved-summaries/',
    views.saved_summaries,
    name='saved_summaries'
),
path(
    'generate-openai/<int:note_id>/',
    views.generate_openai_summary,
    name='generate_openai_summary'
),
path(
    'compare/<int:note_id>/',
    views.compare_summaries,
    name='compare_summaries'
),
     path(
    'download-summary/<int:summary_id>/',
    views.download_summary,
    name='download_summary'
),
path(
    'delete-saved-summary/<int:saved_id>/',
    views.delete_saved_summary,
    name='delete_saved_summary'
),
path(
    'profile/',
    views.profile,
    name='profile'
),
path(
    'profile/edit/',
    views.edit_profile,
    name='edit_profile'
),

path(
    'profile/change-password/',
    views.change_password,
    name='change_password'
),
path(
    'view-note/<int:note_id>/',
    views.view_note,
    name='view_note'
),
path(
    'download-note/<int:note_id>/',
    views.download_note,
    name='download_note'
),
path(
    'delete-note/<int:note_id>/',
    views.delete_note,
    name='delete_note'
),



]