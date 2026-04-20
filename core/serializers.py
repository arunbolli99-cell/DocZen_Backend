from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserActivity

User = get_user_model()

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ('id', 'action_type', 'description', 'related_id', 'timestamp')

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(write_only=True, required=False, source='name')
    recent_activities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'gender', 'date_of_birth', 'recent_activities', 'date_joined', 'profile_pic')

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_recent_activities(self, obj):
        activities = obj.activities.all()[:10]
        return UserActivitySerializer(activities, many=True).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['name'] = self.get_name(instance)
        return ret

    def update(self, instance, validated_data):
        # Handle name if provided
        name = self.initial_data.get('name') or self.initial_data.get('full_name')
        if name:
            name_parts = name.strip().split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        # Handle other fields
        email = validated_data.get('email', instance.email)
        if email != instance.email:
            if User.objects.filter(email=email).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})
            instance.email = email
            instance.username = email

        instance.phone = validated_data.get('phone', instance.phone)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        
        if 'profile_pic' in validated_data:
            instance.profile_pic = validated_data['profile_pic']
            
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'confirm_password', 'phone', 'gender', 'date_of_birth')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered. Please login instead.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        name = validated_data.pop('name')
        # Split name into first and last for AbstractUser compatibility
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        user = User.objects.create_user(
            username=validated_data['email'], # Using email as username
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            gender=validated_data.get('gender', ''),
            date_of_birth=validated_data.get('date_of_birth'),
            first_name=first_name,
            last_name=last_name
        )
        return user
