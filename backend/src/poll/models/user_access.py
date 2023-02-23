from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from poll.models.poll import Poll
from poll.utils import USER_ROLE

User = get_user_model()


class UserAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_access')
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='user_access', db_index=True)
    role = models.CharField(max_length=80, choices=USER_ROLE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'user_poll_access'
        indexes = [
            models.Index(fields=['poll'])
        ]


class Invitations(models.Model):
    email = models.CharField(max_length=200)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='invitations')
    role = models.CharField(max_length=80, choices=USER_ROLE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'invitation_poll_access'
