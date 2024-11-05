from django.urls import path
from .views import URLCreateView

urlpatterns = [
  path('scan-url/', URLCreateView.as_view(), name='scan-url')
]