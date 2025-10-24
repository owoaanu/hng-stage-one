from django.db import models

# Create your models here.

class AnalyzedString(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # sha256
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)