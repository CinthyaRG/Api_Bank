from django.core.validators import RegexValidator
from django.db import models

# Validador para cédula
ID_VALIDATOR = RegexValidator(
    regex=r'^[VEJ]{1}-\d{6,9}$',
    message="Formato de cédula inválido.",
)


class Bank(models.Model):
    name = models.CharField(max_length=150)
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
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    ident = models.CharField(validators=[ID_VALIDATOR], max_length=11, unique=True)
    phone = models.ForeignKey(Phone)
    birthday = models.DateField()

    def get_name(self):
        return self.first_name + " " + self.last_name

    def __str__(self):
        return str(self.ident) + " " + self.first_name + " " + self.last_name


class Product(models.Model):
    customer = models.ForeignKey(Customer)
    num_card = models.CharField(unique=True, max_length=20)
    month = models.CharField(max_length=2)
    year = models.CharField(max_length=2)
    ccv = models.CharField(max_length=3)

    def __str__(self):
        return self.num_card + " (" + self.customer.first_name + \
               " " + self.customer.last_name + ")"


class Balance(models.Model):
    available = models.DecimalField(blank=False, max_digits=30, decimal_places=2)
    deferrer = models.DecimalField(null=True, blank=True, max_digits=30, decimal_places=2, default=0)
    lock = models.DecimalField(null=True, blank=True, max_digits=30, decimal_places=2, default=0)

    def __str__(self):
        return str(self.id) + " (Bs." + str(self.available) + "/ Bs." +\
               str(self.deferrer) + "/ Bs." + str(self.lock) + ")"


class Appointment(models.Model):
    bank = models.ForeignKey(Branch)
    customer = models.ForeignKey(Customer)
    date_appointment = models.DateField()

    def __str__(self):
        return str(self.id) + " (" + str(self.bank) + "/ " +\
               str(self.customer) + " -- " + str(self.date_appointment) + ")"


class Account(models.Model):
    product_bank = [
        ('Cuenta Ahorro', 'Cuenta Ahorro'),
        ('Cuenta Corriente', 'Cuenta Corriente'),
    ]
    product = models.OneToOneField(Product)
    name = models.CharField(choices=product_bank, max_length=16)
    pin = models.CharField(max_length=4)
    numAcc = models.CharField(max_length=20)
    branch = models.ForeignKey(Branch)
    balance = models.ForeignKey(Balance)

    def __str__(self):
        return self.name + " (" + str(self.product) + ")"


class Check(models.Model):
    numCheck = models.IntegerField(unique=True, primary_key=True)
    status = models.BooleanField(default=False)
    account = models.ForeignKey(Account)

    def __str__(self):
        return str(self.numCheck) + " (" + str(self.account) + \
               " -- " + str(self.status) + ")"


class Tdc(models.Model):
    product_bank = [
        ('VISA', 'VISA'),
        ('MASTERCARD', 'MASTERCARD'),
        ('AMERICAN EXPRESS', 'AMERICAN EXPRESS'),
    ]
    name = models.CharField(choices=product_bank, max_length=16)
    product = models.ForeignKey(Product)
    limit = models.DecimalField(max_digits=30, decimal_places=2)
    balance = models.DecimalField(max_digits=30, decimal_places=2)
    status = models.BooleanField()

    def __str__(self):
        return self.name + " (" + str(self.product) + ")"


class Loan(models.Model):
    customer = models.ForeignKey(Customer)
    account = models.ForeignKey(Account)
    numInstallments = models.IntegerField()
    paidInstallments = models.IntegerField()
    overdueInstallments = models.IntegerField()
    startingAmount = models.DecimalField(max_digits=30, decimal_places=2)
    paidAmount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    date = models.DateField()

    def __str__(self):
        return str(self.id) + " (" + str(self.customer) + " -- " + \
               str(self.account) + ")"


class Movement(models.Model):
    ref = models.CharField(unique=True, max_length=30)
    amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    details = models.CharField(max_length=128, blank=True)
    date = models.DateField()

    def __str__(self):
        return self.ref + " (Bs." + str(self.amount) + ")"


class Transaction_Simple(models.Model):
    transaction_type = [
        ('Deposito', 'Depósito'),
        ('Retiro', 'Retiro'),
        ('POS', 'POS'),
    ]
    movement = models.ForeignKey(Movement)
    account = models.ForeignKey(Account, null=True, blank=True)
    tdc = models.ForeignKey(Tdc, null=True, blank=True)
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
