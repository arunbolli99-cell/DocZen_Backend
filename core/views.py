from rest_framework import status, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserActivity
from .serializers import RegisterSerializer, UserSerializer, UserActivitySerializer

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        "status": "success",
        "message": "DocZen API v1 is live!",
        "version": "1.0.0"
    })

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "message": "User registered successfully",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "success": True,
            "user": serializer.data
        })

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Profile updated successfully",
            "user": serializer.data
        })

class UserActivityListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Clear all activities for the user."""
        UserActivity.objects.filter(user=self.request.user).delete()
        return Response({
            "success": True, 
            "message": "All activities cleared successfully."
        }, status=status.HTTP_200_OK)

class UserActivityDestroyView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserActivitySerializer

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
