from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/question/<int:question_id>/', views.question_view, name='question_view'),
    path('result/<int:quiz_id>/', views.result_view, name='result_view'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('stats/', views.stats_view, name='stats'),
    path('result/view/<int:result_id>/', views.result_detail, name='result_detail'),
]