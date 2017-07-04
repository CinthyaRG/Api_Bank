from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from api_app.serializers import *


@ensure_csrf_cookie
def validate_data(request):
    print("ENTRO")
    numtarj = request.POST.get('numtarj', None)
    pin = request.POST.get('pin', None)
    ccv = request.POST.get('ccv', None)
    month = request.POST.get('month', None)
    year = request.POST.get('year', None)
    ci = request.POST.get('ci', None)

    data = {}

    try:
        product = Product.objects.get(num_card=numtarj)
        if (product.month == month) and (product.year == year) and (product.ccv == ccv) :
            try:
                customer = Customer.objects.get(id=product.customer)
                if customer.ident == ci :
                    

    except Product.DoesNotExist:
        data['error'] = 'El número de tarjeta introducido no existe.'

    # data = {
    #     # 'username_exists': Customer.objects.filter(username=username).exists()
    #     'correct': True
    # }
    #
    # if data['correct']:
    #     data['error'] = 'El username escogido no está disponible.'

    return JsonResponse(data)


class CustomersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomersSerializer


class BanksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Bank.objects.all()
    serializer_class = BanksSerializer


class BranchesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Branch.objects.all()
    serializer_class = BranchesSerializer


class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class AccountsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class TdcViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Tdc.objects.all()
    serializer_class = TDCSerializer


class LoansViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer



        #class UsuarioViewSet(viewsets.ModelViewSet):
#    """
#   API endpoint that allows users to be viewed or edited.
#    """
#    queryset = Usuarios.objects.all().ord