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

class StringAnalysis(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # SHA-256 hash
    value = models.TextField(unique=True)
    properties = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'string_analyses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.value[:50]}..."