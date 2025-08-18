from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class MyAccountManager(BaseUserManager):

    def create_user(self, first_name, last_name, username, email, password=None, **extra_fields):

        if not email:
            raise ValueError('User must have have an email address')
        
        if not username:
            raise ValueError('User must have username')
        
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)       
        return user
    
    def create_superuser(self, first_name, last_name, email, username, password=None, **extra_fields):

        user=self.create_user(

            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **extra_fields
        )

        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, email):

        return self.get(email=email)


class Account(AbstractBaseUser, PermissionsMixin):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    username=models.CharField(max_length=50, unique=True)
    email=models.EmailField(max_length=100, unique=True)
    phone_number=models.CharField(max_length=50)

    #required
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)

    #Login fields

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username', 'first_name','last_name']

    objects=MyAccountManager()

    def __str__(self):
        return self.email
    
    def has_perm(self,perm, obj=None):
        return self.is_admin
    
    def has_model_perms(self,add_lable):
        return True

    