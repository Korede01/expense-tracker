from django.db.models import Avg, Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import ExpenseFilter
from .models import Expense
from .reports import generate_spending_chart
from .serializers import ExpenseSerializer
from users.permissions import IsUser


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    CRUD operations and summary for user expenses.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsUser]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter
    ordering_fields = ['date', 'amount']
    ordering = ['-date']

    def get_queryset(self):
        return (
            Expense.objects.filter(user=self.request.user)
            .select_related('user')
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        stats = qs.aggregate(
            total=Sum('amount'),
            average=Avg('amount'),
            count=Count('id')
        )
        return Response({
            'total_expenses': stats['total'] or 0,
            'average_expense': stats['average'] or 0,
            'transaction_count': stats['count'] or 0,
        })


class ExpenseReportView(viewsets.GenericViewSet):
    """Provides report endpoints for expenses."""
    permission_classes = [IsUser]

    @action(detail=False, methods=['get'])
    def spending_chart(self, request):
        chart = generate_spending_chart(request.user)
        return Response({'chart': chart})