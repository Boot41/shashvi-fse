from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Lead, Outreach

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at', 'lead_score')

class OutreachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outreach
        fields = '__all__'
        read_only_fields = ('generated_at',)
