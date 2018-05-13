from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager

# カスタムUserモデルを使う場合だけ、登録する
if settings.AUTH_USER_MODEL == 'cms.User':
    class UserManager(BaseUserManager):
        """ユーザーマネージャー"""
        use_in_migrations = True

        def _create_user(self, email, password, **extra_fields):
            """Create and save a user with the given username, email, and
            password."""
            if not email:
                raise ValueError('The given email must be set')
            email = self.normalize_email(email)

            user = self.model(email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

        def create_user(self, email, password=None, **extra_fields):
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            return self._create_user(email, password, **extra_fields)

        def create_superuser(self, email, password, **extra_fields):
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)

            if extra_fields.get('is_staff') is not True:
                raise ValueError('Superuser must have is_staff=True.')
            if extra_fields.get('is_superuser') is not True:
                raise ValueError('Superuser must have is_superuser=True.')

            return self._create_user(email, password, **extra_fields)


    class User(AbstractBaseUser, PermissionsMixin):
        """カスタムユーザーモデル

        usernameを使わず、emailアドレスをユーザー名として使うようにしています。
        """
        email = models.EmailField(_('email address'), unique=True)
        first_name = models.CharField(_('first name'), max_length=30, blank=True)
        last_name = models.CharField(_('last name'), max_length=150, blank=True)

        is_staff = models.BooleanField(
            _('staff status'),
            default=False,
            help_text=_(
                'Designates whether the user can log into this admin site.'),
        )
        is_active = models.BooleanField(
            _('active'),
            default=True,
            help_text=_(
                'Designates whether this user should be treated as active. '
                'Unselect this instead of deleting accounts.'
            ),
        )
        date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

        objects = UserManager()

        EMAIL_FIELD = 'email'
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []

        class Meta:
            verbose_name = _('user')
            verbose_name_plural = _('users')

        def get_full_name(self):
            """Return the first_name plus the last_name, with a space in
            between."""
            full_name = '%s %s' % (self.first_name, self.last_name)
            return full_name.strip()

        def get_short_name(self):
            """Return the short name for the user."""
            return self.first_name

        def email_user(self, subject, message, from_email=None, **kwargs):
            """Send an email to this user."""
            send_mail(subject, message, from_email, [self.email], **kwargs)

        @property
        def username(self):
            return self.email


    class Person(models.Model):
        """要員モデル"""

        # 名前
        name = models.CharField(max_length=255)
        # メールアドレス
        email = models.CharField(max_length=255, unique=True)

    class Grade(models.Model):
        """グレードモデル"""

        # KSC社員級（同一部署）
        IN_G1 = 1
        IN_G2 = 2
        IN_G3 = 3
        IN_G4 = 4
        IN_G5 = 5
        IN_G6 = 6
        IN_G7 = 7

        # KSC社員級（他部署）
        OUT_G1 = 11
        OUT_G2 = 12
        OUT_G3 = 13
        OUT_G4 = 14
        OUT_G5 = 15
        OUT_G6 = 16
        OUT_G7 = 17


        # グレード
        grade = models.IntegerField()
        # 適用開始年月
        start_ym = models.DateTimeField()
        # 適用終了年月
        end_ym = models.DateTimeField(null=True, blank=True)


    class Cost(models.Model):
        """コストモデル"""

        # 人
        person = models.ForeignKey(Person, related_name='costs',  on_delete=models.CASCADE)
        # 所属会社
        company = models.IntegerField()
        # 社員等級
        grade = models.ForeignKey(Grade, related_name='grades', on_delete=models.CASCADE)
        # 部署区分
        busho_kbn = models.IntegerField(default=1, choices=[(1, '製造第一'), (2, '他部署')])
        # 外注費
        cost = models.IntegerField()
        # 適用開始年月
        start_ym = models.DateTimeField()
        # 適用終了年月
        end_ym = models.DateTimeField(null=True, blank=True)
        # 実績フラグ
        yojitsu_kbn = models.IntegerField(default=1, choices=[(1, '予定'), (2, '実績')])

