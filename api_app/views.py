from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from api_app.serializers import *


@ensure_csrf_cookie
def validate_data(request):
    print("ENTRO")
    print(request.POST)
    print(request.GET)
    numtarj = request.GET.get('numtarj', None)
    pin = request.GET.get('pin', None)
    ccv = request.GET.get('ccv', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    ci = request.GET.get('ci', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {
        'product': Product.objects.filter(num_card=numtarj).exists()
    }

    if data['product']:
        product = Product.objects.get(num_card=numtarj)
        if (product.month == month) and (product.year == year) and (product.ccv == ccv):
            data['customer'] = Customer.objects.filter(id=product.customer.id).exists()
            data['account'] = Account.objects.filter(product=product.id).exists()
            if data['customer'] and data['account']:
                customer = Customer.objects.get(id=product.customer.id)
                accounts = Account.objects.filter(product=product.id)
                if customer.ident == ci:
                    for a in accounts:
                        if a.pin == pin:
                            data['correct'] = True
                            data['customer_name'] = customer.first_name
                            data['customer_last'] = customer.last_name
                            data['customer_ident'] = customer.ident
                            break
                        else:
                            data['correct'] = False
                else:
                    data['correct'] = False
            else:
                data['correct'] = False
        else:
            data['correct'] = False
    else:
        data['correct'] = False

    if not(data['correct']):
        data['error'] = msj_error

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