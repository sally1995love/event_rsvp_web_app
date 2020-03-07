from django.urls import path, include
from django.contrib.auth import logout, login
from . import views
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required

app_name = 'rsvp'
"""
urlpatterns = [
    #ex: /polls/
    path('', views.index, name='index'),
    #ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    #ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    #ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]
"""
urlpatterns = [
    path('accounts/signup/', views.SignUp, name='signup'),
    # rsvp/profile
    path('profile/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    # rsvp/events
    path('events_owner/', views.EventOwnerView.as_view(), name = 'event_owner'),
    path('events_vendor/', views.EventVendorView.as_view(), name = 'event_vendor'),
    path('events_guest/', views.EventGuestView.as_view(), name = 'event_guest'),

    path('events_owner/<int:pk>/', views.EventOwnerDetailView.as_view(), name = 'event_owner_detail'),
    path('events_vendor/<int:pk>/', views.EventVendorDetailView.as_view(), name = 'event_vendor_detail'),
    path('events_guest/<int:pk>/', views.event_guest_detail, name = 'event_guest_detail'),
    
    path('events_create/<int:user_id>/', views.event_create, name = 'event_create'),
    path('<int:event_id>/permissions_create/', views.permission_create, name = 'permission_create'),
    path('<int:event_id>/question_create/', views.question_create, name = 'question_create'),
    path('<int:question_id>/question_create/choice_create_index', views.choice_create_index, name = 'choice_create_index'),
    path('<int:question_id>/question_create/choice_create', views.choice_create, name = 'choice_create'),
    path('<int:event_id>/question_create_index/', views.question_create_index, name = 'question_create_index'),
    path('<int:question_id>/question_revise/', views.question_revise, name='question_revise'),
    path('<int:question_id>/question_delete/', views.question_delete, name='question_delete'),
    path('<int:choice_id>/choice_revise/', views.choice_revise, name='choice_revise'),
    path('<int:choice_id>/choice_delete/', views.choice_delete, name='choice_delete'),
    path('<int:permission_id>/guest_answer_index/', views.guest_answer_index, name='guest_answer_index'),
    path('<int:event_id>/notify_question', views.notify_question, name='notify_question'),
    path('<int:choice_id>/notify_choice', views.notify_choice, name='notify_choice'),
    path('<int:question_id>/guest_answer/', views.guest_answer, name='guest_answer'),
    path('<int:question_id>/question_stop/', views.question_stop, name='question_stop'),
    path('<int:response_id>/answer_revise/', views.answer_revise, name='answer_revise'),
    path('<int:question_id>/guest_answer_new/', views.guest_answer_new, name='guest_answer_new'),
    
]
 
