from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Session(models.Model):
    url = models.TextField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="study_session"
    )
    description = models.TextField(max_length=255)
    cards = models.JSONField(null=True)

    def __str__(self):
        return f"{self.description}"


# Create a card model here
class Card(models.Model):
    question = models.TextField(max_length=1000)
    answer = models.TextField(max_length=1000)
    session = models.ForeignKey("Session", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card")
    state = models.CharField(
        max_length=50, default="pending"
    )  # will either be "pending", "useless", "done"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.question}"
