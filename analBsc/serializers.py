from rest_framework import serializers
from django.contrib.auth.models import User

from .models import AddressInfo, Profile, Admin


class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressInfo
        fields = '__all__'


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer):
    # tracks = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['last_login', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'admin']
        depth = 1
