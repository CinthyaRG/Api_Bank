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
    profile = request.GET.get('profile', None)
    msj_error = 'Los datos introducidos no son correctos, por favor verifíquelos'

    data = {'product': Product.objects.filter(numCard=numtarj).exists(),
            'ccv': True,
            'month': True,
            'year': True,
            'pin': True,
            'ci': True}

    if data['product']:

        product = Product.objects.get(numCard=numtarj)

        if ((product.month == month) and (product.year == year) and (product.ccv == ccv)) or not(profile is None):
            data['customer'] = Customer.objects.filter(id=product.customer.id).exists()
            data['account'] = Account.objects.filter(product=product.id).exists()
            if data['customer'] and data['account'] or not(profile is None):
                customer = Customer.objects.get(id=product.customer.id)
                accounts = Account.objects.filter(product=product.id)
                if customer.ident == ci or not(profile is None):
                    for a in accounts:
                        if a.pin == pin or not(profile is None):
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

    print(data)
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


def conv_balance(a):
    a = str(a).split('.')
    b = a[0][::-1]
    l = len(b)
    i = 0
    j = 3
    amount = ''
    while i < l:
        if j >= l:
            amount = amount + b[i:l]
        else:
            amount = amount + b[i:j] + '.'
        i = i + 3
        j = j + 3
    amount = amount[::-1]
    if len(a) == 2:
        amount = amount + ',' + a[1][:2]
    else:
        amount = amount + ',00'
    return amount


@ensure_csrf_cookie
def data_customer(request):
    print(request.method.lower() != "options")

    num = request.GET.get('num', None)
    option = request.GET.get('option', 0)
    select = request.GET.get('select', '0')
    startDate = request.GET.get('start', None)
    endDate = request.GET.get('end', None)

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'account': [],
            'tdc': [],
            'loan': [],
            'mov_acc': [[], []],
            'mov_tdc': [[], [], []]
            }

    if request.method.lower() != "options":
        print('entro')
        if data['product']:
            product = Product.objects.get(numCard=num)
            customer = Customer.objects.get(pk=product.customer.id)
            accounts = Account.objects.filter(product=product.id).order_by('name')
            products = Product.objects.filter(customer=customer.id).exclude(numCard=num)
            loans = Loan.objects.filter(customer=customer.id)

            for a in accounts:

                details_acc = ['Cuenta ' + a.name,
                               a.numAcc[:10] + "******" + a.numAcc[16:],
                               "Activa",
                               [conv_balance(a.balance.available), conv_balance(a.balance.deferrer),
                                conv_balance(a.balance.lock)],
                               a.branch.name]

                data['account'].append(details_acc)

                if option == 'consultar-cuenta':
                    if startDate is None and endDate is None:
                        today = datetime.datetime.today()
                        end_day = calendar.monthrange(today.year, today.month)[1]
                        start = str(today.year) + '-' + str(today.month) + '-1'
                        if today.day == end_day:
                            today = today + datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = str(today.year) + '-0' + str(today.month) + '-' + str(today.day + 1)
                    else:
                        today = startDate.split('/')
                        end_date = endDate.split('/')
                        end_day = calendar.monthrange(int(today[2]), int(today[1]))[1]
                        start = today[2] + '-' + today[1] + '-' + today[0]
                        if int(end_date[0]) == end_day:
                            today = datetime.date(int(end_date[2]), int(end_date[1]), int(end_date[0])) + \
                                    datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = end_date[2] + '-' + end_date[1] + '-' + str((int(end_date[0]) + 1))

                    if select != '0':
                        select.replace('ó', 'o')

                        trans_simple = TransactionSimple.objects.filter(account=a.pk,
                                                                        type=select,
                                                                        movement__date__range=[start, end])

                        transf_out = TransferServices.objects.filter(accSource=a.pk,
                                                                     type=select,
                                                                     movement__date__range=[start, end]).order_by('id')

                        transf_in = TransferServices.objects.filter(accDest=a.pk,
                                                                    type=select,
                                                                    movement__date__range=[start, end]).order_by('id')

                        payments = PaymentTlf.objects.filter(account=a.pk,
                                                             type=select,
                                                             movement__date__range=[start, end]).order_by('id')
                    else:
                        trans_simple = TransactionSimple.objects.filter(account=a.pk,
                                                                        movement__date__range=[start, end])

                        transf_out = TransferServices.objects.filter(accSource=a.pk,
                                                                     movement__date__range=[start, end]).order_by('id')

                        transf_in = TransferServices.objects.filter(accDest=a.pk,
                                                                    movement__date__range=[start, end]).order_by('id')

                        payments = PaymentTlf.objects.filter(account=a.pk,
                                                             movement__date__range=[start, end]).order_by('id')

                    transaction = transf_out | transf_in

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
                                       sig + conv_balance(mov.amount),
                                       conv_balance(t.amountResult)]

                        if t.type == 'Pagos':
                            if t.tdc is None:
                                details = mov.details
                            else:
                                details = mov.details + ' --Pago de TDC ' + t.tdc.name + \
                                          ' perteneciente a ' + t.tdc.product.customer.get_name()
                        else:
                            details = mov.details

                        details_mov.append(details)

                        data['mov_acc'][i].append(details_mov)

                    for tr in transaction:
                        mov = Movement.objects.get(pk=tr.movement.id)
                        if tr.type == 'Pagos':
                            w = 'o'
                        else:
                            w = 'a'
                        details_mov = [mov.date,
                                       mov.ref,
                                       tr.get_type_display()]

                        if tr.accDest.id == a.id:
                            details_mov.append('+' + conv_balance(mov.amount))
                            details_mov.append(conv_balance(tr.amountDest))
                            details = mov.details + ' --' + tr.get_type_display() + ' recibid' + w \
                                      + ' de la cuenta de ' + tr.accSource.product.customer.get_name()
                        else:
                            details_mov.append('-' + conv_balance(mov.amount))
                            details_mov.append(conv_balance(tr.amountSource))
                            if tr.accDest is None:
                                details = mov.details
                            else:
                                details = mov.details + ' --' + tr.get_type_display() + ' realizad' + \
                                          w + ' a la cuenta de ' + tr.accDest.product.customer.get_name()

                        details_mov.append(details)

                        data['mov_acc'][i].append(details_mov)

                    for p in payments:
                        mov = Movement.objects.get(pk=p.movement.id)
                        details_mov = [mov.date,
                                       mov.ref,
                                       p.type,
                                       '-' + conv_balance(mov.amount),
                                       conv_balance(p.amountResult),
                                       mov.details + ' --Recarga a operadora ' +
                                       p.get_operator_display() + ' al número (' + p.numTlf + ')']
                        data['mov_acc'][i].append(details_mov)

                    data['mov_acc'][i].sort(reverse=True)

            for p in products:
                tdc = Tdc.objects.get(product=p.id)
                payment = TransactionSimple.objects.filter(tdc=tdc.pk, type='Pagos').order_by('-movement')[0]
                movement = Movement.objects.get(pk=payment.movement.pk)
                details_tdc = [tdc.name,
                               p.numCard[:4] + "********" + p.numCard[12:],
                               movement.date,
                               conv_balance(movement.amount),
                               conv_balance(tdc.balance),
                               conv_balance(tdc.balanceAvailable),
                               conv_balance(tdc.minimumPayment),
                               tdc.date,
                               conv_balance(tdc.limit)]
                if tdc.status:
                    details_tdc.insert(2, 'Activa')
                else:
                    details_tdc.insert(2, 'Inactiva')

                data['tdc'].append(details_tdc)

                if option == 'consultar-tdc':
                    if startDate is None and endDate is None:
                        today = datetime.datetime.today()
                        end_day = calendar.monthrange(today.year, today.month)[1]
                        start = str(today.year) + '-' + str(today.month) + '-1'
                        if today.day == end_day:
                            today = today + datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = str(today.year) + '-0' + str(today.month) + '-' + str(today.day + 1)
                    else:
                        today = startDate.split('/')
                        end_date = endDate.split('/')
                        end_day = calendar.monthrange(int(today[2]), int(today[1]))[1]
                        start = today[2] + '-' + today[1] + '-' + today[0]
                        if int(end_date[0]) == end_day:
                            today = datetime.date(int(end_date[2]), int(end_date[1]), int(end_date[0])) + \
                                    datetime.timedelta(days=1)
                            end = str(today.year) + '-' + str(today.month) + '-' + str(today.day)
                        else:
                            end = end_date[2] + '-' + end_date[1] + '-' + str((int(end_date[0]) + 1))

                    if select != '0':
                        trans_simple = TransactionSimple.objects.filter(tdc=tdc.pk,
                                                                        type=select,
                                                                        movement__date__range=[start, end])
                    else:
                        trans_simple = TransactionSimple.objects.filter(tdc=tdc.pk,
                                                                        movement__date__range=[start, end])

                    if tdc.name == 'VISA':
                        i = 0
                    elif tdc.name == 'MASTERCARD':
                        i = 1
                    else:
                        i = 2

                    for t in trans_simple:
                        mov = Movement.objects.get(pk=t.movement.id)
                        if t.type == 'Pagos':
                            sig = '+'
                        else:
                            sig = '-'
                        details_mov = [mov.date,
                                       t.get_type_display(),
                                       sig + conv_balance(mov.amount)]

                        data['mov_tdc'][i].append(details_mov)

                    data['mov_tdc'][i].sort(reverse=True)

            for l in loans:
                details_loan = [conv_int('PRESTAMO') + str(l.id),
                                'Cuenta ' + l.account.name + ' ****' + l.account.numAcc[16:],
                                conv_balance(l.paidAmount),
                                l.date_payment,
                                l.numInstallments,
                                conv_balance(l.startingAmount),
                                conv_balance(l.overdue_amount),
                                l.date,
                                l.date_expires,
                                l.paidInstallments,
                                l.overdueInstallments]

                data['loan'].append(details_loan)

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


@ensure_csrf_cookie
def send_transfer(request):
    acc_source = request.GET.get('acc_source', None).split(' ')
    acc_dest = request.GET.get('acc_dest', None).split(' ')
    amount = decimal.Decimal(request.GET.get('amount', None))
    num = request.GET.get('num', None)
    type = request.GET.get('type', None)
    name = 'TRANSFERENCIA'

    data = {'product': Product.objects.filter(numCard=num).exists(),
            'success': False,
            'msg': 'Ha ocurrido un error validando sus datos'
            }

    if request.method.lower() != "options":
        if data['product']:
            product = Product.objects.get(numCard=num)
            s = Account.objects.filter(name=acc_source[0],
                                       numAcc__endswith=acc_source[1].replace('*', '')).exists()
            d = Account.objects.filter(name=acc_dest[0],
                                       numAcc__endswith=acc_dest[1].replace('*', '')).exists()

            if type == 'transf-mis-cuentas':
                if s and d:
                    source = Account.objects.filter(name=acc_source[0],
                                                    numAcc__endswith=acc_source[1].replace('*', ''))[0]
                    dest = Account.objects.filter(name=acc_dest[0],
                                                  numAcc__endswith=acc_dest[1].replace('*', ''))[0]
                    if source.product.customer_id == dest.product.customer_id:
                        if source.product.customer_id == product.customer_id:
                            bs = Balance.objects.get(pk=source.balance_id)
                            bd = Balance.objects.get(pk=dest.balance_id)

                            bs.available = bs.available - amount
                            bd.available = bd.available + amount

                            num = TransferServices.objects.filter(type=name.capitalize()).count()

                            mov = Movement(ref=conv_int(name)+str(num+1),
                                           amount=amount,
                                           details='Transferencia entre sus cuentas',
                                           date=datetime.datetime.today())
                            mov.save()
                            transf = TransferServices(type=name.capitalize(),
                                                      movement=mov,
                                                      accSource=source,
                                                      accDest=dest,
                                                      amountSource=bs.available,
                                                      amountDest=bd.available)
                            transf.save()
                            bs.save()
                            bd.save()
                            data['success'] = True
                            data['msg'] = 'Transferencia realizada satisfactoriamente.'

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
