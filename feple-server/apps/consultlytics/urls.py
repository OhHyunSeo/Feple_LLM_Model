from django.urls import path
from . import views

app_name = 'consultlytics'

urlpatterns = [
    path('analyze/<str:call_id>/', views.analyze_consulting, name='analyze_consulting'),
] 