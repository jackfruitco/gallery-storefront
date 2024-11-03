from django.shortcuts import render, get_object_or_404
from django.views import generic
# from apps.main.models import Profile
from apps.gallery.models import Project

def index(request):
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    def get_queryset():
        """Return the last five published questions."""
        return Project.objects.order_by("-created_at")[:4]

    return render(request,
                  'main/index.html',
                  {"project_list": get_queryset()},
                  )

def redirect(request):
    return redirect("/home")

#class AboutView(generic.DetailView):
    # model = Profile
    # context_object_name = "profile"
    # queryset = Profile.objects.get(id=1)
    #template_name = "main/about_index.html"

    #def get_queryset(self):
    #    self.profile = get_object_or_404(Profile, slug=self.kwargs["slug"])
    #    # return Profile.objects.filter(id=self.profile.id)
    #    return Profile.objects.filter(id=1)

    #def get_context_data(self, **kwargs):
    #    # Call the base implementation first to get a context
    #    context = super().get_context_data(**kwargs)
    #    # Add in the publisher
    #    context["profile"] = self.profile
    #    return context