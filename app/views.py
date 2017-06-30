from django.shortcuts import render
from app.models import *
from rest_framework import viewsets
from app.serializers import CustomersSerializer


class CustomersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Customers.objects.all()
    serializer_class = CustomersSerializer

#class UsuarioViewSet(viewsets.ModelViewSet):
#    """
#   API endpoint that allows users to be viewed or edited.
#    """
#    queryset = Usuarios.objects.all().ord