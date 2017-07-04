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
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {
        'correct': False
    }

    print(request.POST)
    print(request.GET)

    try:
        product = Product.objects.get(num_card=numtarj)
        if (product.month == month) and (product.year == year) and (product.ccv == ccv):
            try:
                customer = Customer.objects.get(id=product.customer)
                accounts = Account.objects.filter(product=product.id)
                if customer.ident == ci:
                    for a in accounts:
                        if a.pin == pin:
                            data['correct'] = True
            except Customer.DoesNotExist:
                pass
            except Account.DoesNotExist:
                pass
    except Product.DoesNotExist:
        pass

    if not(data['correct']):
        data['error'] = msj_error

    print(data)

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


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