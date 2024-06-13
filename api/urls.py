from django.urls import path
from api import views
from rest_framework.documentation import include_docs_urls
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Get all sessions - ListCreate
    path("sessions/", views.SessionCreate.as_view()),
    # Get a particular session - RetrieveDestroy
    path("sessions/<int:pk>/", views.SessionDetail.as_view()),
    # Get only cards of a particular session - List
    path("sessions/<int:pk>/cards/", views.CardsOfSession.as_view()),
    # Get a specific card for a specific session - RetrieveDestroy
    path("sessions/<int:session>/cards/<int:pk>/", views.CardOfSession.as_view()),
    # Get all cards for the user - List
    path("cards/", views.AllCards.as_view()),
    # Get a particular card - Retrieve
    path("cards/<int:pk>/", views.CardDetail.as_view()),
    # Documentation
    path("docs/", include_docs_urls(title="Sessions and Cards API")),
]

urlpatterns = format_suffix_patterns(urlpatterns)
