from django.core.management.base import BaseCommand
from django.utils import timezone
from base.models import PendingUser  # ← Ensure this matches your app name!
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes PendingUser records older than 2 minutes'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(minutes=2)
        
        # Debug: Print cutoff time and records to be deleted
        print(f"Cutoff time: {cutoff}")
        old_users = PendingUser.objects.filter(created_at__lt=cutoff)
        print(f"Found {old_users.count()} users to delete:")
        for user in old_users:
            print(f"  - ID: {user.id}, Created: {user.created_at}")
        
        deleted_count, _ = old_users.delete()
        print(f"Successfully deleted {deleted_count} pending users")