import django_filters
from django.core.exceptions import ValidationError

from .models import Expense


class ExpenseFilter(django_filters.FilterSet):
    """
    Filters for Expense list by date range, category, and amount range.
    """
    start_date = django_filters.DateFilter(
        field_name='date', lookup_expr='gte', label='Start Date'
    )
    end_date = django_filters.DateFilter(
        field_name='date', lookup_expr='lte', label='End Date'
    )
    category = django_filters.ChoiceFilter(
        field_name='category', choices=Expense.CATEGORIES
    )
    min_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte', label='Min Amount'
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte', label='Max Amount'
    )

    class Meta:
        model = Expense
        fields = ['category', 'start_date', 'end_date', 'min_amount', 'max_amount']

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        sd = self.data.get('start_date')
        ed = self.data.get('end_date')

        if sd and ed and sd > ed:
            raise ValidationError('Start date must be before end date.')
        return qs