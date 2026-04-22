from rest_framework import status, generics, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .models import UserActivity, OTP
from .serializers import RegisterSerializer, UserSerializer, UserActivitySerializer
from .utils import send_otp_email

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
class SendOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email:
            return Response({"success": False, "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Security check: If user exists, they MUST provide the correct password before we send an OTP
        try:
            user = User.objects.get(email=email)
            if not password:
                return Response({"success": False, "message": "Password is required for existing accounts"}, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(password):
                return Response({"success": False, "message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            # New user, no password check needed yet (they will register via OTP)
            pass

        # Generate 6-digit OTP
        otp_code = str(random.randint(100000, 999999))
        
        # Save OTP to database
        OTP.objects.create(email=email, code=otp_code)
        
        # Send Email
        sent = send_otp_email(email, otp_code)
        
        if sent:
            return Response({"success": True, "message": f"Verification code sent to {email}"})
        else:
            return Response({"success": False, "message": "Failed to send OTP. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({"success": False, "message": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the latest unverified OTP for this email
        otp_record = OTP.objects.filter(email=email, code=code, is_verified=False).last()
        
        if not otp_record:
            return Response({"success": False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_record.is_expired():
            return Response({"success": False, "message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as verified
        otp_record.is_verified = True
        otp_record.save()

        # Get or create user
        user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "success": True,
            "message": "Logged in successfully" if not created else "Registered and logged in successfully",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
