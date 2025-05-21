from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Expense(models.Model):
    """
    Tracks user expenses with categories, amounts, and timestamps.
    """
    CATEGORIES = [
        ('GROCERIES', 'Groceries'),
        ('UTILITIES', 'Utilities'),
        ('ENTERTAINMENT', 'Entertainment'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORIES
    )
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['category']),
        ]
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - ${self.amount} on {self.date}"