from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Session, Card
from .utils import cardify_pdf
import json


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        # No one can read the password
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class SessionSerializer(serializers.ModelSerializer):
    requirement = serializers.CharField(write_only=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "url",
            "created_at",
            "description",
            "author",
            "cards",
            "requirement",
        ]
        extra_kwargs = {
            "description": {"read_only": True},
            "cards": {"read_only": True},
            "author": {"read_only": True},
        }

    def create(self, validated_data):
        requirement = validated_data.pop("requirement")
        session_instance = Session(**validated_data)
        output = cardify_pdf(remote_url=validated_data["url"], requirement=requirement)
        session_instance.description = output["description"]
        session_instance.cards = output["cards"]
        session_instance.save()

        for card in output["cards"]:
            Card.objects.create(
                question=card["question"],
                answer=card["answer"],
                session=session_instance,
                author=session_instance.author,
            )
        return session_instance


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "author",
            "created_at",
            "session",
            "question",
            "answer",
            "state",
        ]
        extra_kwargs = {"author": {"read_only": True}}
