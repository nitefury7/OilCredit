from django.db import models


class Gender(models.IntegerChoices):
    MALE, FEMALE, OTHER = range(3)
