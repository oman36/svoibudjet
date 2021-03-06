from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=255)
    inn = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('Category', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '[%s] %s' % (self.shop.name, self.name,)

    class Meta:
        unique_together = ('shop', 'name',)


class Check(models.Model):
    date = models.DateTimeField(null=False, unique=True)
    discount = models.FloatField(default=0)
    discount_sum = models.FloatField(default=0)
    total_sum = models.FloatField(null=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return '%s %s' % (self.shop.__str__(), self.date)


class Item(models.Model):
    check_model = models.ForeignKey(Check, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.FloatField(null=False)
    sum = models.FloatField(null=False)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return '%s  %.3f x %.2f' % (self.product.name, self.quantity, self.price)


class QRData(models.Model):
    check_model = models.ForeignKey(Check, on_delete=models.SET_NULL, null=True)
    qr_string = models.CharField(max_length=255, null=False, unique=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(null=False, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __str__(self):
        return str(self.qr_string)
