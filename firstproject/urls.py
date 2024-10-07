from django.urls import path
from . import views

urlpatterns = [
    path('blog', views.ContactListCreateView.as_view()),
    path('blog/<str:pk>/', views.ContactRetrieveUpdateDeleteView.as_view()),
]