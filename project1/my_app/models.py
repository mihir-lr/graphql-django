from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', null=True, blank=True)

    def __str__(self):
        return self.title

    def number_of_likes(self):
        return self.likes.count()