from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Expense

User = get_user_model()


class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for Expense model ensuring data validity and formatting.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = ['id', 'user', 'amount', 'category', 'date', 'description']
        read_only_fields = ['id', 'user']
        extra_kwargs = {
            'amount': {'min_value': 0.01},
            'date': {'format': '%Y-%m-%d'},
        }

    def validate_amount(self, value):
        if not (0 < value <= 1_000_000):
            raise serializers.ValidationError(
                'Amount must be greater than zero and at most 1,000,000.'
            )
        return value

    def validate_date(self, value):
        today = timezone.now().date()
        oldest = today - timezone.timedelta(days=365 * 5)

        if value > today:
            raise serializers.ValidationError('Future dates are not allowed.')
        if value < oldest:
            raise serializers.ValidationError('Date cannot be older than 5 years.')
        return value

    def validate_category(self, value):
        valid = [choice[0] for choice in Expense.CATEGORIES]
        upper = value.upper()
        if upper not in valid:
            raise serializers.ValidationError(
                f'Invalid category. Choose from: {', '.join(valid)}'
            )
        return upper

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['amount'] = f"{instance.amount:.2f}"
        rep['date'] = instance.date.strftime('%Y-%m-%d')
        return rep