from django.urls import path
from .views import organizations, discrepancies
urlpatterns = [path('organizations/', organizations), path('discrepancies/', discrepancies)]
