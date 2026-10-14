from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .scrapers.postjobfree_llm import search_and_process
import logging

logger = logging.getLogger(__name__)

class CandidateSearchView(APIView):
    def post(self, request):
        all_words = str(request.data.get('all_words') or request.data.get('skill') or '').strip()
        experience = str(request.data.get('experience') or '').strip()
        location = str(request.data.get('location') or 'India').strip()
        params = {
            "all_words": all_words,
            "experience": experience,
            "location": location,
            "radius": request.data.get('radius', 50),
            "limit": request.data.get('limit', 10)
        }

        if not params['all_words']:
             return Response(
                 {"error": "Skill parameter is required."}, 
                 status=400
             )

        try:
            data = search_and_process(params)
            
            result = {
                "status": "success",
                "count": len(data),
                "candidates": data
            }
            return Response(result)

        except Exception as e:
            logger.error(f"View Error: {e}")
            return Response({"error": "Internal Server Error"}, status=500)

def dashboard(request):
    return render(request, 'index.html')


def candidate_detail(request):
    return render(request, 'detail.html')