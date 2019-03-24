from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import datetime
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank = True)
    picture = models.ImageField(upload_to='profile_images', blank = True)

    def __unicode__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views =models.IntegerField(default=0)
    likes =models.IntegerField(default=0)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural='categories'

    def save(self, *args, **kwargs):
        #if self.id is None:
        self.slug = slugify(self.name)
        if self.views < 0:
            self.views = 0
        if self.likes < 0:
            self.likes = 0
        super(Category, self).save(*args, **kwargs)

    def __unicode__(self):  #For Python 2, use __str__ on Python 3
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    first_visit = models.DateTimeField(default = datetime.datetime.now, editable=False)
    last_visit = models.DateTimeField(default = datetime.datetime.now)

    def __unicode__(self):      #For Python 2, use __str__ on Python 3
        return self.title

    def save(self, *args, **kwargs):
        if self.last_visit < self.first_visit:
            self.last_visit = self.first_visit
        super(Page, self).save(*args, **kwargs)
