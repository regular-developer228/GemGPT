from django.db import models

# Create your models here.
class Conversation(models.Model):
    session_key = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation #{self.id}"

class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'пользователь'),
        ('assistant', 'ассистент')
    ]

    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"