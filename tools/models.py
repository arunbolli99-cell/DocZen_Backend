from django.db import models
from django.conf import settings
import string
import random

class VoiceToolHistory(models.Model):
    TOOL_CHOICES = (
        ('tts', 'Text to Speech'),
        ('stt', 'Speech to Text'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_history')
    tool_type = models.CharField(max_length=10, choices=TOOL_CHOICES)
    input_data = models.TextField()  # Input text for TTS or transcription for STT
    voice_used = models.CharField(max_length=50, null=True, blank=True)
    output_result = models.JSONField() # Transcribed text for STT or Audio URL hint for TTS
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('model', 'AI Assistant'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.email} ({self.role}): {self.text[:30]}..."

class TextToolHistory(models.Model):
    TOOL_CHOICES = (
        ('summarize', 'Summarizer'),
        ('grammar', 'Grammar Checker'),
        ('explain-code', 'Code Explainer'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='text_history')
    tool_type = models.CharField(max_length=20, choices=TOOL_CHOICES)
    input_text = models.TextField()
    output_result = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class ImageToolHistory(models.Model):
    TOOL_CHOICES = (
        ('ai-generate', 'Image Generator'),
        ('ai-detect', 'Image Detector'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='image_history')
    tool_type = models.CharField(max_length=20, choices=TOOL_CHOICES)
    input_data = models.TextField(null=True, blank=True)  # Prompt or image URL
    output_result = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class ResumeAnalysisHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_history')
    resume_name = models.CharField(max_length=255)
    job_description = models.TextField()
    analysis_result = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
