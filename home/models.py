from django.db import models
import datetime
from django.utils import timezone


# Create your models here.

class Symbol(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    market = models.CharField(max_length=20)
    asset_type = models.IntegerField()
    ipo_date = models.DateField()
    delisting_date = models.DateField()
    status = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # sector = models.CharField(max_length=50)
    # industry = models.CharField(max_length=50)
    # country = models.CharField(max_length=50)
    # market_cap = models.FloatField()
    # pe_ratio = models.FloatField()
    # dividend_yield = models.FloatField()
    # beta = models.FloatField()
    # price = models.FloatField()
    # change = models.FloatField()
    # volume = models.FloatField()
    # avg_volume = models.FloatField()
    # exchange = models.CharField(max_length=50)
    # description = models.TextField()
    # website = models.URLField()

    def __str__(self):
        return f"{self.symbol} - {self.name}"


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
