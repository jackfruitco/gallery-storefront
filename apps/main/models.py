from django.db import models
from django.conf import settings
from autoslug import AutoSlugField

# class Profile(models.Model):
#    first_name = models.CharField(max_length=50)
#    middle_name = models.CharField(max_length=50, blank=True)
#    last_name = models.CharField(max_length=50)
#
#    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True)
#
#    position = models.CharField(max_length=50, blank=True)
#
#    quote = models.TextField(blank=True)
#    about_me = models.TextField(blank=True)
#    portrait = models.ImageField(upload_to='media/images/profiles/', blank=True)
#
#    display_on_home = models.BooleanField(default=True)
#    active = models.BooleanField(default=True)
#
#    data_verified = models.DateTimeField(auto_now=True)
#
#    def full_name(self):
#        if self.middle_name: return f"{self.first_name} {self.middle_name} {self.last_name}"
#        else: return f"{self.first_name} {self.last_name}"
#
#    def first_mi_last(self):
#        mi = self.middle_name[:1]
#        if self.middle_name: return f"{ self.first_name } { mi } { self.last_name }"
#        else: return f"{self.first_name} {self.last_name}"
#
#    slug = AutoSlugField(populate_from='first_mi_last', unique=True, always_update=True, editable=True)
#
#    def __str__(self):
#        return self.full_name()
#
# class Contact(models.Model):
#    contact_name = models.ForeignKey(Profile, on_delete=models.CASCADE)
#    contact_type = {
#        "email": "Email",
#        "phone": "Phone",
#        "website": "Website",
#        "instagram": "Instagram",
#    }
#    contact_data = models.TextField()
#    contact_created_at = models.DateTimeField(auto_now_add=True)
#    contact_modified_at = models.DateTimeField(auto_now=True)

#    def __str__(self):
#        return f"{self.contact_name}_{self.contact_data}"
