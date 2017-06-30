from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models

# Validador para cédula
ID_VALIDATOR = RegexValidator(
    regex=r'^[VE]{1}-\d{6,8}$',
    message="Formato de cédula inválido.",
)


class Bank(models.Model):
    name = models.CharField(max_length=150)
    cod = models.IntegerField(blank=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'cod')


class Branches(models.Model):
    name = models.CharField(unique=True, max_length=64)
    bank = models.ForeignKey(Bank)

    def __str__(self):
        return self.name


class Customers(models.Model):
    user = models.OneToOneField(User)
    ident = models.CharField(validators=[ID_VALIDATOR], primary_key=True, max_length=10)
    bank = models.ManyToManyField(Bank, through='Product')

    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    def __str__(self):
        return str(self.id) + " " + self.user.first_name + " " + self.user.last_name


class Appointment(models.Model):
    bank = models.ForeignKey(Branches)
    customer = models.ForeignKey(Customers)
    date_appointment = models.DateField()


class Product(models.Model):
    bank = models.ForeignKey(Bank)
    customer = models.ForeignKey(Customers)
    num_card = models.CharField(unique=True, max_length=20)
    month = models.IntegerField()
    year = models.IntegerField()
    ccv = models.IntegerField()

    def __str__(self):
        return self.bank.name + "(" + self.customer.user.first_name + \
               self.customer.user.last_name + ")"


class Balances(models.Model):
    available = models.IntegerField(blank=False)
    deferrer = models.IntegerField(blank=True)
    lock = models.IntegerField(blank=True)


class Account(models.Model):
    product_bank = [
        ('Cuenta Ahorro', 'Cuenta Ahorro'),
        ('Cuenta Corriente', 'Cuenta Corriente'),
    ]
    product = models.ForeignKey(Product)
    name = models.CharField(choices=product_bank, max_length=16)
    pin = models.IntegerField()
    num_acc = models.CharField(max_length=20)
    branch = models.ForeignKey(Branches)
    balances = models.ForeignKey(Balances)

    def __str__(self):
        return self.name + "(" + self.num_acc + ")"


class Check(models.Model):
    num_check = models.IntegerField(unique=True, primary_key=True)
    status = models.BooleanField()
    account = models.ForeignKey(Account)


class Tdc(models.Model):
    product_bank = [
        ('VISA', 'VISA'),
        ('MASTERCARD', 'MASTERCARD'),
        ('AMERICAN EXPRESS', 'AMERICAN EXPRESS'),
    ]
    name = models.CharField(choices=product_bank, max_length=16)
    product = models.ForeignKey(Product)
    limit = models.IntegerField(blank=False)
    balance = models.IntegerField()
    status = models.BooleanField()


class Loans(models.Model):
    product = models.ForeignKey(Product)
    num_installments = models.IntegerField()
    paid_installments = models.IntegerField()
    overdue_installments = models.IntegerField()
    starting_amount = models.IntegerField()
    paid_amount = models.IntegerField()
    date = models.DateField()


class Movement(models.Model):
    ref = models.CharField(unique=True, max_length=30)
    amount = models.IntegerField()
    details = models.CharField(max_length=128, blank=True)
    date = models.DateField()


class Transaction_Simple(models.Model):
    transaction_type = [
        ('Deposito', 'Depósito'),
        ('Retiro', 'Retiro'),
        ('POS', 'POS'),
    ]
    movement = models.ForeignKey(Movement)
    account = models.ForeignKey(Account)
    type = models.CharField(choices=transaction_type, max_length=10)


class Transfer_Services(models.Model):
    transaction_type = [
        ('Pagos', 'Pagos'),
        ('Transferencia', 'Transferencia'),
    ]
    movement = models.ForeignKey(Movement)
    acc_source = models.ForeignKey(Account, related_name="acc_source")
    acc_dest = models.ForeignKey(Account, related_name="acc_dest")
    type = models.CharField(choices=transaction_type, max_length=13)


class Payments_Tdc(models.Model):
    movement = models.ForeignKey(Movement)
    account = models.ForeignKey(Account)
    card_dest = models.ForeignKey(Tdc)


class Payments_Tlf(models.Model):
    operator = [
        ('CANTV', 'CANTV'),
        ('DIGITEL', 'DIGITEL'),
        ('MOVILNET', 'MOVILNET'),
        ('MOVISTAR', 'MOVISTAR'),
    ]
    movement = models.ForeignKey(Movement)
    account = models.ForeignKey(Account)
    operator = models.CharField(choices=operator, max_length=10)
    num_tlf = models.CharField(max_length=11)
