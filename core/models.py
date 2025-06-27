# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='student', **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, role='superadmin', **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_encoder(self, email, password=None, **extra_fields):
        user = self.create_user(email, password, role='encoder', **extra_fields)
        user.is_staff = True  # Optional: encoders may or may not be staff
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('encoder', 'Encoder'),
        ('student', 'Student'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Common fields
    full_name = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class EncoderProfile(models.Model):
    ENCODER_TYPE_CHOICES = [
        (1, 'Student Registration'),
        (2, 'Games'),
        (3, 'Videos and Images'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='encoder_profile')
    phone_number = models.CharField(max_length=20)
    university = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    additional_notes = models.TextField(blank=True, null=True)
    encoder_type = models.PositiveSmallIntegerField(choices=ENCODER_TYPE_CHOICES)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_encoders')
    # 'created_by' will be the superadmin who created this encoder

    def __str__(self):
        return f"{self.user.full_name} ({self.get_encoder_type_display()})"

class StudentProfile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    image = models.ImageField(upload_to='students/images/', blank=True, null=True)
    course_program = models.CharField(max_length=255)  # You can replace with ForeignKey if you have Course model
    graduation_year = models.PositiveSmallIntegerField()
    bio = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_students')  # Encoder who registered the student
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_students')  # Superadmin who approved student

    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.full_name