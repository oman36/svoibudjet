from django.db import models


class Check(models.Model):
    date = models.DateTimeField(null=False)
    discount = models.FloatField(default=0)
    discount_sum = models.FloatField(default=0)
    total_sum = models.IntegerField(null=False)
    user = models.CharField(max_length=255)
    user_inn = models.IntegerField()

    def __str__(self):
        return 'Sum: %s [%s]' % (self.total_sum, self.date.isoformat())


class Item(models.Model):
    check = models.ForeignKey(Check, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.FloatField(null=False)
    quantity = models.FloatField(null=False)
    sum = models.FloatField(null=False)
