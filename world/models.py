from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField


class City(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    name = models.CharField(db_column='Name', max_length=35)
    countrycode = models.ForeignKey('Country', models.DO_NOTHING, db_column='CountryCode')
    district = models.CharField(db_column='District', max_length=20)
    population = models.IntegerField(db_column='Population')

    class Meta:
        managed = False
        db_table = 'city'


class Country(models.Model):
    code = models.CharField(db_column='Code', primary_key=True, max_length=3)
    name = models.CharField(db_column='Name', max_length=52)
    continent = models.CharField(db_column='Continent', max_length=13)
    region = models.CharField(db_column='Region', max_length=26)
    surfacearea = models.FloatField(db_column='SurfaceArea')
    indepyear = models.SmallIntegerField(db_column='IndepYear', blank=True, null=True)
    population = models.IntegerField(db_column='Population')
    lifeexpectancy = models.FloatField(db_column='LifeExpectancy', blank=True, null=True)
    gnp = models.FloatField(db_column='GNP', blank=True, null=True)
    gnpold = models.FloatField(db_column='GNPOld', blank=True, null=True)
    localname = models.CharField(db_column='LocalName', max_length=45)
    governmentform = models.CharField(db_column='GovernmentForm', max_length=45)
    headofstate = models.CharField(db_column='HeadOfState', max_length=60, blank=True, null=True)
    capital = models.IntegerField(db_column='Capital', blank=True, null=True)
    code2 = models.CharField(db_column='Code2', max_length=2)

    class Meta:
        managed = False
        db_table = 'country'


class Countrylanguage(models.Model):
    countrycode = models.ForeignKey(Country, models.DO_NOTHING, db_column='CountryCode', primary_key=True)
    language = models.CharField(db_column='Language', max_length=30)
    isofficial = models.CharField(db_column='IsOfficial', max_length=1)
    percentage = models.FloatField(db_column='Percentage')

    class Meta:
        managed = False
        db_table = 'countrylanguage'
        unique_together = (('countrycode', 'language'),)

    def __str__(self):
        # Replaced Python 2 __unicode__ with __str__ for Python 3 compatibility
        return "country-code: %s language: %s" % (self.countrycode.name, self.language)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class MyCustomUserManager(BaseUserManager):
    def create_user(self, email_id, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email_id:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email_id),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name=None):
        u = self.create_user(
            email_id=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        u.is_superuser = True
        u.is_staff = True
        u.save(using=self._db)
        return u


class User(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=100, default="female")
    email = models.CharField(max_length=100, primary_key=True)
    phone_number = PhoneNumberField(blank=True)

    objects = MyCustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]
