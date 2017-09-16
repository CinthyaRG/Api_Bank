
from django.core.validators import RegexValidator, MaxValueValidator
from django.db import models
import decimal
import datetime

# Validador para cédula
ID_VALIDATOR = RegexValidator(
    regex=r'^[VEJ]{1}-\d{6,9}$',
    message="Formato de cédula inválido.",
)


class Bank(models.Model):
    name = models.CharField(max_length=128)
    cod = models.CharField(blank=False, max_length=4)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'cod')


class Phone(models.Model):
    home = models.CharField(max_length=12, null=True)
    cellphone = models.CharField(max_length=12, null=True)
    office = models.CharField(max_length=12, null=True)


class Branch(models.Model):
    name = models.CharField(max_length=64)
    bank = models.ForeignKey(Bank)
    phone = models.ForeignKey(Phone)

    def __str__(self):
        return self.name


class Customer(models.Model):
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    ident = models.CharField(validators=[ID_VALIDATOR], max_length=11, unique=True)
    birthday = models.DateField()
    phone = models.ForeignKey(Phone)

    def get_name(self):
        return self.firstName + " " + self.lastName

    def __str__(self):
        return str(self.ident) + " " + self.firstName + " " + self.lastName


class Product(models.Model):
    numCard = models.CharField(unique=True, max_length=20)
    month = models.CharField(max_length=2)
    year = models.CharField(max_length=2)
    ccv = models.CharField(max_length=3)
    customer = models.ForeignKey(Customer)

    def __str__(self):
        return self.numCard + " (" + self.customer.firstName + \
               " " + self.customer.lastName + ")"


class Balance(models.Model):
    available = models.DecimalField(blank=False, max_digits=30, decimal_places=2)
    deferrer = models.DecimalField(null=True, blank=True, max_digits=30, decimal_places=2, default=0)
    lock = models.DecimalField(null=True, blank=True, max_digits=30, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id) + " (Bs." + str(self.available) + "/ Bs." + \
               str(self.deferrer) + "/ Bs." + str(self.lock) + ")"


class Appointment(models.Model):
    dateAppointment = models.DateField()
    bank = models.ForeignKey(Branch)
    customer = models.ForeignKey(Customer)

    def __str__(self):
        return str(self.id) + " (" + str(self.bank) + "/ " + \
               str(self.customer) + " -- " + str(self.dateAppointment) + ")"


class Account(models.Model):
    product_bank = [
        ('Ahorro', 'Ahorro'),
        ('Corriente', 'Corriente'),
    ]
    name = models.CharField(choices=product_bank, max_length=16)
    pin = models.CharField(max_length=4)
    numAcc = models.CharField(max_length=20)
    product = models.ForeignKey(Product)
    branch = models.ForeignKey(Branch)
    balance = models.ForeignKey(Balance)

    def __str__(self):
        return self.name + " (" + str(self.product) + ")"

    class Meta:
        ordering = ["name"]


class Checkbook(models.Model):
    numCheckbook = models.IntegerField(unique=True, primary_key=True)
    status = models.BooleanField(default=False)
    numCheck = models.PositiveSmallIntegerField(validators=[MaxValueValidator(50)])
    account = models.ForeignKey(Account)

    def __str__(self):
        return str(self.numCheckbook) + " (" + str(self.account) + \
               " -- " + str(self.status) + " -- " + str(self.numCheck) + ")"


class Tdc(models.Model):
    product_bank = [
        ('VISA', 'VISA'),
        ('MASTERCARD', 'MASTERCARD'),
        ('AMERICAN EXPRESS', 'AMERICAN EXPRESS'),
    ]
    name = models.CharField(choices=product_bank, max_length=16)
    limit = models.DecimalField(max_digits=30, decimal_places=2)
    balance = models.DecimalField(max_digits=30, decimal_places=2)
    status = models.BooleanField()
    date = models.DateField()
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.name + " (" + str(self.product) + ")"

    def get_available(self):
        return self.limit - self.balance

    def get_min(self):
        a = self.balance * decimal.Decimal('0.01')
        b = (self.balance - a) * decimal.Decimal('0.0392')

        return round(a + b, 2)

    balanceAvailable = property(get_available)
    minimumPayment = property(get_min)


class Loan(models.Model):
    numInstallments = models.PositiveSmallIntegerField(validators=[MaxValueValidator(36)])
    paidInstallments = models.PositiveSmallIntegerField(validators=[MaxValueValidator(36)])
    overdueInstallments = models.PositiveSmallIntegerField(validators=[MaxValueValidator(36)])
    startingAmount = models.DecimalField(max_digits=30, decimal_places=2)
    paidAmount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    date = models.DateField()
    date_payment = models.DateField()
    customer = models.ForeignKey(Customer)
    account = models.ForeignKey(Account)

    def __str__(self):
        return str(self.id) + " (" + str(self.customer) + " -- " + \
               str(self.account) + ")"

    def overdue_amount(self):
        return round(self.startingAmount - self.paidAmount, 2)

    def get_amount(self):
        a = self.startingAmount * decimal.Decimal('0.29')
        amount = round((self.startingAmount + a) / self.numInstallments, 2)

        return amount

    def date_expires(self):
        a = self.numInstallments
        today = self.date
        month = today.month + (a % 12)
        year = a // 12

        if month > 12:
            year = year + 1
            month = (a % 12) - (12 - today.month)

        return datetime.datetime(today.year+year, month, today.day)

    overdue_amount = property(overdue_amount)
    date_expires = property(date_expires)
    amount_installments = property(get_amount)


class Movement(models.Model):
    ref = models.CharField(unique=True, max_length=30)
    amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    details = models.CharField(max_length=256, blank=True)
    date = models.DateTimeField()

    def __str__(self):
        return self.ref + " (Bs." + str(self.amount) + ")"

    class Meta:
        ordering = ["date"]


class TransactionSimple(models.Model):
    transaction_type = [
        ('Deposito', 'Depósito'),
        ('Retiro', 'Retiro'),
        ('POS', 'POS'),
        ('Pagos', 'Pagos'),
        ('Comision', 'Comisión')
    ]
    type = models.CharField(choices=transaction_type, max_length=10)
    movement = models.ForeignKey(Movement)
    amountResult = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    account = models.ForeignKey(Account, null=True, blank=True)
    tdc = models.ForeignKey(Tdc, null=True, blank=True)

    def __str__(self):
        return self.type + ' ' + str(self.movement)


class TransferServices(models.Model):
    transaction_type = [
        ('Pagos', 'Pagos'),
        ('Transferencia', 'Transferencia'),
    ]
    type = models.CharField(choices=transaction_type, max_length=13)
    movement = models.ForeignKey(Movement)
    amountSource = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    amountDest = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    accSource = models.ForeignKey(Account, related_name="accSource")
    accDest = models.ForeignKey(Account, related_name="accDest", null=True, blank=True)

    def __str__(self):
        return str(self.id) + ': Origen ->' + str(self.accSource.product.customer) + ' Destino ->' + str(self.accDest.product.customer)

    class Meta:
        ordering = ["id"]


# class PaymentTdc(models.Model):
#     movement = models.ForeignKey(Movement)
#     account = models.ForeignKey(Account)
#     card_dest = models.ForeignKey(Tdc)


class PaymentTlf(models.Model):
    operator = [
        ('CANTV', 'CANTV'),
        ('DIGITEL', 'DIGITEL'),
        ('MOVILNET', 'MOVILNET'),
        ('MOVISTAR', 'MOVISTAR'),
    ]
    operator = models.CharField(choices=operator, max_length=10)
    type = models.CharField(default='Pagos', max_length=5)
    numTlf = models.CharField(max_length=12)
    amountResult = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    movement = models.ForeignKey(Movement)
    account = models.ForeignKey(Account)
