from django.contrib import admin
from django.urls import path
# Import the new candidate_detail view
from api.views import CandidateSearchView, dashboard, candidate_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend Dashboard
    path('', dashboard, name='home'),
    
    # NEW: Detail Page Route
    path('candidate/detail', candidate_detail, name='candidate_detail'),
    
    # API Endpoint
    path('api/candidates/search', CandidateSearchView.as_view(), name='search'),
]