from django.urls import path
from .views import CandidateSearchView

urlpatterns = [
    # This points to the new Class-based view we created
    path('candidates/search', CandidateSearchView.as_view(), name='search_candidates'),
]