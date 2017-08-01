import calendar

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from api_app.serializers import *
import datetime


@ensure_csrf_cookie
def validate_data(request):
    numtarj = request.GET.get('numtarj', None)
    pin = request.GET.get('pin', None)
    ccv = request.GET.get('ccv', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    ci = request.GET.get('ci', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {'product': Product.objects.filter(numCard=numtarj).exists(),
            'ccv': True,
            'month': True,
            'year': True,
            'pin': True,
            'ci': True}

    if data['product']:

        product = Product.objects.get(numCard=numtarj)

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
                            data['customer_name'] = customer.firstName
                            data['customer_last'] = customer.lastName
                            data['customer_ident'] = customer.ident

                            if customer.phone.home is None:
                                data['phone_home'] = "None-None"
                            else:
                                data['phone_home'] = customer.phone.home

                            if customer.phone.cellphone is None:
                                data['cellphone'] = "None-None"
                            else:
                                data['cellphone'] = customer.phone.cellphone

                            if customer.phone.office is None:
                                data['phone_office'] = "None-None"
                            else:
                                data['phone_office'] = customer.phone.office

                            data['birthday'] = customer.birthday
                            break
                        else:
                            data['correct'] = False
                            data['pin'] = False
                else:
                    data['correct'] = False
                    data['ci'] = False
            else:
                data['correct'] = False
        else:
            data['correct'] = False

            if product.month != month:
                data['month'] = False
            if product.year != year:
                data['year'] = False
            if product.ccv != ccv:
                data['ccv'] = False
    else:
        data['correct'] = False

    if not (data['correct']):
        data['error'] = msj_error

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


def conv_int(cadena):
    s = ''
    for c in cadena:
        s = s + str(ord(c))
        if len(s) == 6:
            return s
    return s


@ensure_csrf_cookie
def data_customer(request):
    num = request.GET.get('num', None)
    print(num)

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'account': [],
            'tdc': [],
            'loan': [],
            'mov': [[], []]
            }

    if data['product']:
        product = Product.objects.get(numCard=num)
        customer = Customer.objects.get(pk=product.customer.id)
        accounts = Account.objects.filter(product=product.id).order_by('name')
        products = Product.objects.filter(customer=customer.id).exclude(numCard=num)
        loans = Loan.objects.filter(customer=customer.id)

        today = datetime.datetime.today()
        end_day = calendar.monthrange(today.year, today.month)[1]

        for a in accounts:
            trans_simple = TransactionSimple.objects.filter(account=a.pk,
                                                            movement__date__gte=datetime.date(today.year, today.month,
                                                                                              1),
                                                            movement__date__lte=datetime.date(today.year, today.month,
                                                                                              end_day))

            transf_out = TransferServices.objects.filter(accSource=a.pk,
                                                         movement__date__gte=datetime.date(today.year, today.month, 1),
                                                         movement__date__lte=datetime.date(today.year, today.month,
                                                                                           end_day)).order_by('id')

            transf_in = TransferServices.objects.filter(accDest=a.pk,
                                                        movement__date__gte=datetime.date(today.year, today.month, 1),
                                                        movement__date__lte=datetime.date(today.year, today.month,
                                                                                          end_day)).order_by('id')

            transaction = transf_out | transf_in

            payments = PaymentTlf.objects.filter(account=a.pk,
                                                 movement__date__gte=datetime.date(today.year, today.month, 1),
                                                 movement__date__lte=datetime.date(today.year, today.month,
                                                                                   end_day)).order_by('id')

            if a.name == 'Ahorro':
                i = 0
            else:
                i = 1

            for t in trans_simple:
                mov = Movement.objects.get(pk=t.movement.id)
                if t.type == 'Deposito':
                    sig = '+'
                else:
                    sig = '-'
                details_mov = [mov.date,
                               mov.ref,
                               t.get_type_display(),
                               sig + str(mov.amount),
                               t.amountResult]

                if t.type == 'Pagos':
                    if t.tdc is None:
                        details = mov.details
                    else:
                        details = mov.details + ' --Pago de TDC ' + t.tdc.name + \
                                  ' perteneciente a ' + t.tdc.product.customer.get_name()
                else:
                    details = mov.details

                details_mov.append(details)

                data['mov'][i].append(details_mov)

            for tr in transaction:
                mov = Movement.objects.get(pk=tr.movement.id)
                if tr.type == 'Pagos':
                    w = 'o'
                else:
                    w = 'a'
                details_mov = [mov.date,
                               mov.ref,
                               tr.get_type_display(),
                               '+' + str(mov.amount)]

                if tr.accDest.id == a.id:
                    details_mov.append(tr.amountDest)
                    details = mov.details + ' --' + tr.get_type_display() + ' recibid' +\
                        w + ' de la cuenta de ' + tr.accSource.product.customer.get_name()
                else:
                    details_mov.append(tr.amountSource)
                    if tr.accDest is None:
                        details = mov.details
                    else:
                        details = mov.details + ' --' + tr.get_type_display() + ' realizad' +\
                            w + ' a la cuenta de ' + tr.accDest.product.customer.get_name()

                details_mov.append(details)

                data['mov'][i].append(details_mov)

            for p in payments:
                mov = Movement.objects.get(pk=p.movement.id)
                details_mov = [mov.date,
                               mov.ref,
                               'Pagos',
                               '-' + str(mov.amount),
                               p.amountResult,
                               mov.details + ' --Recarga a operadora ' +
                               p.get_operator_display() + ' al número (' + p.numTlf + ')']
                data['mov'][i].append(details_mov)

            data['mov'][i].sort(reverse=True)

            details_acc = ['Cuenta ' + a.name,
                           a.numAcc[:10] + "******" + a.numAcc[16:],
                           "Activa",
                           [a.balance.available, a.balance.deferrer, a.balance.lock],
                           a.branch.name]

            data['account'].append(details_acc)

        for p in products:
            tdc = Tdc.objects.get(product=p.id)
            details_tdc = [tdc.name,
                           p.numCard[:4] + "********" + p.numCard[12:],
                           tdc.balance,
                           tdc.date]

            data['tdc'].append(details_tdc)

        for l in loans:
            details_loan = [conv_int('PRESTAMO') + str(l.id),
                            'Cuenta ' + l.account.name + ' *****' + l.account.numAcc[16:],
                            l.paidAmount, l.date]

            data['loan'].append(details_loan)

    print(data['mov'])

    response = JsonResponse(data)
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS,GET,PUT,POST,DELETE'
    response['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type, X-CSRFToken'

    return response


@ensure_csrf_cookie
def validate_data_forgot(request):
    numtarj = request.GET.get('numtarj', None)
    ccv = request.GET.get('ccv', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    ci = request.GET.get('ci', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {'product': Product.objects.filter(numCard=numtarj).exists(),
            'ccv': True,
            'month': True,
            'year': True,
            'ci': True}

    if data['product']:
        product = Product.objects.get(numCard=numtarj)
        if (product.month == month) and (product.year == year) and (product.ccv == ccv):
            data['customer'] = Customer.objects.filter(id=product.customer.id).exists()
            if data['customer']:
                customer = Customer.objects.get(id=product.customer.id)
                if customer.ident == ci:
                    data['correct'] = True
                    data['customer_name'] = customer.firstName
                    data['customer_last'] = customer.lastName
                    data['customer_ident'] = customer.ident

                    if customer.phone.home is None:
                        data['phone_home'] = "None-None"
                    else:
                        data['phone_home'] = customer.phone.home

                    if customer.phone.cellphone is None:
                        data['cellphone'] = "None-None"
                    else:
                        data['cellphone'] = customer.phone.cellphone

                    if customer.phone.office is None:
                        data['phone_office'] = "None-None"
                    else:
                        data['phone_office'] = customer.phone.office

                    data['birthday'] = customer.birthday
                else:
                    data['correct'] = False
                    data['ci'] = False
            else:
                data['correct'] = False
        else:
            data['correct'] = False
            if product.month != month:
                data['month'] = False
            if product.year != year:
                data['year'] = False
            if product.ccv != ccv:
                data['ccv'] = False
    else:
        data['correct'] = False

    if not (data['correct']):
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

    # class UsuarioViewSet(viewsets.ModelViewSet):
    #    """
    #   API endpoint that allows users to be viewed or edited.
    #    """
    #    queryset = Usuarios.objects.all().ord
