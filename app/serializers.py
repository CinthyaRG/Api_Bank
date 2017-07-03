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


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'customer', 'num_card', 'month', 'year', 'ccv')


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Account
        fields = ('url', 'product', 'name', 'num_acc')


class TDCSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tdc
        fields = ('url', 'product', 'name', 'status')


class LoanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Loan
        fields = ('url', 'customer', 'account', 'starting_amount')
