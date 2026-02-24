from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# USER MANAGER

class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, role='user')
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )

        user.role = 'admin'
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
# USER MODEL 

class User(AbstractBaseUser):

    ROLE_CHOICE = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICE,
        default='user'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.email


    # Permissions

    def has_perm(self, perm, obj=None):
        return self.is_admin


    def has_module_perms(self, app_label):
        return self.is_admin