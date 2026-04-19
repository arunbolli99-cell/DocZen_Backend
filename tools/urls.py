from django.urls import path
from .views import (
    ResumeAnalyzerView, AIChatView, ChatHistoryView, VoiceToolView, VoiceHistoryView,
    TextToolView, ImageToolView, ImageProxyView,
    ResumeHistoryView, TextHistoryView, ImageHistoryView
)

urlpatterns = [
    path('resume/analyze/', ResumeAnalyzerView.as_view(), name='resume-analyze'),
    path('resume/history/', ResumeHistoryView.as_view(), name='resume-history'),
    path('resume/history/<int:pk>/', ResumeHistoryView.as_view(), name='resume-history-detail'),
    path('ai-chat/', AIChatView.as_view(), name='ai-chat'),
    path('ai-chat/history/', ChatHistoryView.as_view(), name='chat-history'),
    path('voice/history/', VoiceHistoryView.as_view(), name='voice-history'),
    path('voice/history/<int:pk>/', VoiceHistoryView.as_view(), name='voice-history-detail'),
    path('voice/<str:tool_type>/', VoiceToolView.as_view(), name='voice-tool'),
    path('text/history/', TextHistoryView.as_view(), name='text-history-all'),
    path('text/history/detail/<int:pk>/', TextHistoryView.as_view(), name='text-history-detail'),
    path('text/history/<str:tool_type>/', TextHistoryView.as_view(), name='text-history'),
    path('text/<str:tool_type>/', TextToolView.as_view(), name='text-tool'),
    path('image/proxy/', ImageProxyView.as_view(), name='image-proxy'),
    path('image/history/', ImageHistoryView.as_view(), name='image-history-all'),
    path('image/history/detail/<int:pk>/', ImageHistoryView.as_view(), name='image-history-detail'),
    path('image/history/<str:tool_type>/', ImageHistoryView.as_view(), name='image-history'),
    path('image/<str:tool_type>/', ImageToolView.as_view(), name='image-tool'),
]
