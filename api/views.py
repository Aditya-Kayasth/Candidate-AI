from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .services import search_candidates_core
import json

class CandidateSearchView(APIView):
    def post(self, request):
        # Extract payload
        skill = request.data.get('skill')
        experience = request.data.get('experience')
        location = request.data.get('location', 'remote')
        limit = request.data.get('limit', 5)

        if not skill:
            return Response({"error": "Skill required"}, status=400)

        # Call Service
        result = search_candidates_core(skill, experience, location, limit=limit)

        # Parse JSON string from AI if success
        if result.get('status') == 'success':
            try:
                result['data'] = json.loads(result['data'])
            except:
                pass # Return raw text if JSON parse fails

        return Response(result)

# We will use this in the next commit
def dashboard(request):
    return render(request, 'index.html')