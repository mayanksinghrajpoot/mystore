from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes unverified users with expired OTPs (older than 1 hour)'

    def handle(self, *args, **kwargs):
        threshold = timezone.now() - timedelta(hours=1)
        # Find users who are inactive AND have an OTP creation time older than threshold
        expired_users = User.objects.filter(
            is_active=False,
            profile__otp_created_at__lt=threshold
        )
        
        count = expired_users.count()
        if count > 0:
            expired_users.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} expired unverified users.'))
        else:
            self.stdout.write(self.style.SUCCESS('No expired unverified users found.'))
