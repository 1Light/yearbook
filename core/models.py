# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from shortuuid.django_fields import ShortUUIDField
from cloudinary.models import CloudinaryField

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
        ('highschool_admin', 'High School Admin'),
        ('college_admin', 'College Admin'),
        ('university_admin', 'University Admin'),
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

class AdminProfile(models.Model):
    INSTITUTION_TYPE_CHOICES = [
        ('highschool', 'High School'),
        ('college', 'College'),
        ('university', 'University'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPE_CHOICES)
    institution_name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_admins')  # the superadmin

    def __str__(self):
        return f"{self.user.full_name} ({self.institution_type})"

class EncoderProfile(models.Model):
    ENCODER_TYPE_CHOICES = [
        (1, 'Student Registration'),
        (2, 'Games'),
        (3, 'Videos and Images'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='encoder_profile')
    encoderId = ShortUUIDField(unique=True, length=10, max_length=21, prefix="encoder", alphabet="ABCDEF0123456789")
    # Add this field:
    institution_type = models.CharField(max_length=20, choices=AdminProfile.INSTITUTION_TYPE_CHOICES)

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
    studentId = ShortUUIDField(unique=True, length=10, max_length=21, prefix="student", alphabet="ABCDEF0123456789")

    # Required fields
    department = models.CharField(max_length=255, blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    graduation_year = models.PositiveSmallIntegerField(blank=True, null=True)
    quote = models.CharField(max_length=255)
    best_memory = models.TextField()
    bio = models.TextField()

    # Optional fields
    nickname = models.CharField(max_length=100, blank=True, null=True)
    future_goal = models.TextField(blank=True, null=True)

    image = CloudinaryField('image', blank=True, null=True)
    course_program = models.CharField(max_length=255, blank=True, null=True)  # Or ForeignKey to Course
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_students')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_students')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.full_name if self.user else "Unnamed Student"

class StudentComment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # the commenter
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.full_name} on {self.student.user.full_name}"

class StudentLike(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # the liker
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'user')  # Prevent double-liking

    def __str__(self):
        return f"{self.user.full_name} liked {self.student.user.full_name}"
    
class StudentShare(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # the one who shared
    platform = models.CharField(max_length=50, blank=True, null=True)  # e.g., "email", "facebook"
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} shared {self.student.user.full_name}"
