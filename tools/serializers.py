from rest_framework import serializers
from .models import ChatMessage, TextToolHistory, ImageToolHistory, ResumeAnalysisHistory, VoiceToolHistory

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('id', 'role', 'text', 'timestamp')

class TextToolHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TextToolHistory
        fields = ('id', 'tool_type', 'input_text', 'output_result', 'timestamp')

class ImageToolHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageToolHistory
        fields = ('id', 'tool_type', 'input_data', 'output_result', 'timestamp')

class ResumeAnalysisHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysisHistory
        fields = ('id', 'resume_name', 'job_description', 'analysis_result', 'timestamp')

class VoiceToolHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceToolHistory
        fields = ('id', 'tool_type', 'input_data', 'voice_used', 'output_result', 'timestamp')
