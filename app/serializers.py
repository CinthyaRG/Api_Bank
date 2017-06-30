from app.models import *
from rest_framework import serializers


class CustomersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customers
        fields = ('url', 'first_name', 'last_name', 'cedula')
