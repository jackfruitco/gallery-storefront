# from django.db.models import F
# from django.http import HttpResponseRedirect
# from django.shortcuts import get_object_or_404, render
# from django.urls import reverse
from django.views import generic

from .models import Project, ProjectImage


# Create your views here.
class IndexView(generic.ListView):
    template_name = "gallery/index.html"
    context_object_name = "project_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Project.objects.filter(display=True).order_by("-created_at")[:16]

class DetailView(generic.DetailView):
    template_name = "gallery/detail.html"
    model = Project