import django_filters
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
# from apps.home.models import Profile
from autoslug import AutoSlugField

def get_image_path(instance, filename):
    return "images/projects/{0}/{1}".format(instance.fk_project.pk, instance.slug + "." + filename.split('.')[-1])

class ProjectType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100, blank=True)
    type = models.ManyToManyField(ProjectType)
    description = models.TextField(blank=True)

    display = models.BooleanField(default=True, help_text="Display this project in website gallery")
    available_for_sale = models.BooleanField(default=False)

    primary_color = models.ForeignKey(Color, on_delete=models.CASCADE)

    created_at = models.DateTimeField(default=timezone.now)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def get_key_image(self):
        return ProjectImage.objects.filter(fk_project=self, key_image=True).first()
    def get_images(self):
        return ProjectImage.objects.filter(fk_project=self.pk).filter(key_image=False).all()[:4]

    def __str__(self):
        return self.name


class ProjectImage(models.Model):
    fk_project = models.ForeignKey(Project, on_delete=models.CASCADE)
    key_image = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(default=10)
    description = models.CharField(max_length=100, blank=False,
                                   help_text="3-5 words describing the image")
    slug = AutoSlugField(populate_from='description', unique_with='fk_project', always_update=True)
    # credit = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to=get_image_path)

    def __str__(self):
        return self.description

    class ProductFilter(django_filters.FilterSet):
        name = django_filters.CharFilter(lookup_expr='ic')
