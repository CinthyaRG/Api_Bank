from app.models import *
from rest_framework import serializers


class CustomersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ('url', 'first_name', 'last_name', 'ident')


class BanksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bank
        fields = ('url', 'name', 'cod')


class BranchesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Branch
        fields = ('url', 'name', 'bank')
