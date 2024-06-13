from django.shortcuts import render
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Session, Card
from .serializers import SessionSerializer, CardSerializer
from rest_framework.exceptions import NotFound

# Create your views here.


# USER VIEWS
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# SESSION EXCLUSIVE VIEWS
class SessionCreate(generics.ListCreateAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Session.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class SessionDetail(generics.RetrieveDestroyAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Session.objects.all()


# CARDS EXCLUSIVE VIEWS - regardless of the session
class AllCards(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Card.objects.filter(author=user)


class CardDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    queryset = Card.objects.all()


# CARDS THROUGH SESSION
class CardsOfSession(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs["pk"]
        return Card.objects.filter(session=session_id)


class CardOfSession(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        session_id = self.kwargs["session"]
        card_id = self.kwargs["pk"]
        try:
            return Card.objects.get(session=session_id, id=card_id)
        except Card.DoesNotExist:
            raise NotFound(detail="Card not found")
