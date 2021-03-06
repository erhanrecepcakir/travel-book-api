from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Category(models.Model):
    """Category to be used for a place"""
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    """Place object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE
    )
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        blank=True,
        null=True
    )
    longitude = models.DecimalField(
        max_digits=22,
        decimal_places=16,
        blank=True,
        null=True
    )
    avg_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True
    )
    notes = models.TextField(max_length=1000, blank=True)
    external_source = models.URLField(blank=True)
    categories = models.ManyToManyField('Category')

    def __str__(self):
        return self.name


class Visit(models.Model):
    """Visit object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE
    )
    title = models.CharField(max_length=255, blank=True)
    place = models.ForeignKey(Place, models.CASCADE)
    time = models.DateField(
        auto_now=False,
        auto_now_add=False,
        blank=True, null=True
    )
    score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True
    )
    notes = models.TextField(max_length=1000, blank=True)

    def __str__(self):
        return self.title


class Plan(models.Model):
    """Plan object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE
    )
    name = models.CharField(max_length=255)
    begins = models.DateField(auto_now=False, auto_now_add=False)
    ends = models.DateField(auto_now=False, auto_now_add=False)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    done = models.BooleanField(default=False)
    visits = models.ManyToManyField('Visit')

    def __str__(self):
        return self.name
