from django.urls import path
from .views import CandidateSearchView, dashboard, candidate_detail 

urlpatterns = [
    # API
    path('candidates/search', CandidateSearchView.as_view(), name='search_candidates'),
    
    # Frontend Pages
    path('', dashboard, name='home'),
    path('candidate/detail', candidate_detail, name='candidate_detail'),
]