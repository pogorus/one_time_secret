from rest_framework import serializers

from secret.models import Secret


class SecretSerializer(serializers.ModelSerializer):
    class Meta:
        model = Secret
        fields = ['id', 'text', 'secret_phrase', 'created_at', 'time_to_live']
