from datetime import datetime, timedelta

from cryptography.fernet import InvalidToken
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from secret.models import Secret
from secret.serializers import SecretSerializer
from secret.crypto import encrypt_text, decrypt_text


class PostSecretView(APIView):
    def post(self, request):
        if not request.data.get('text'):
            return Response({'Error': 'Text is missing'}, status=status.HTTP_400_BAD_REQUEST)
        encrypted_data = request.data.copy()
        encrypted_data['text'] = encrypt_text(encrypted_data['text'])
        if request.data.get('secret_phrase'):
            encrypted_data['secret_phrase'] = encrypt_text(encrypted_data['secret_phrase'])
        serializer = SecretSerializer(data=encrypted_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            latest_secret = Secret.objects.latest('id')
            secret_key = encrypt_text(str(latest_secret.id))
            return Response({'secret key': secret_key}, status=status.HTTP_201_CREATED)

class GetSecretView(APIView):
    def get(self, request, secret_key):
        try:
            decrypted_secret_key = decrypt_text(secret_key)
            secret = Secret.objects.get(id=decrypted_secret_key)
            if secret.time_to_live and secret.created_at + timedelta(seconds=secret.time_to_live) < timezone.now():
                secret.delete()
                raise LookupError
        except (InvalidToken, ObjectDoesNotExist, LookupError):
            return Response({'Error': {'Secret has already been read or never existed'}},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = SecretSerializer(secret)
        data = serializer.data
        data['text'] = decrypt_text(data['text'])
        if not secret.secret_phrase == '':
            if decrypt_text(secret.secret_phrase) == request.GET.get('secret_phrase'):
                secret.delete()
                return Response({'text': data['text']}, status=status.HTTP_200_OK)
            return Response({'Secret phrase': 'is needed'}, status=status.HTTP_403_FORBIDDEN)
        secret.delete()
        return Response({'text': data['text']}, status=status.HTTP_200_OK)

class GetAllSecretsView(APIView):
    def get(self, request):
        secrets = Secret.objects.all()
        serializer = SecretSerializer(secrets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

