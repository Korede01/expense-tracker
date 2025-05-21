from io import BytesIO
import base64

import matplotlib.pyplot as plt
from django.db.models import Sum

from .models import Expense


def generate_spending_chart(user):
    """
    Returns a base64-encoded PNG of spending totals per category.
    """
    qs = (
        Expense.objects.filter(user=user)
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    if not qs:
        return None

    cats = [item['category'] for item in qs]
    amts = [float(item['total']) for item in qs]

    plt.figure(figsize=(10, 6))
    plt.bar(cats, amts)
    plt.title('Spending Distribution')
    plt.xlabel('Category')
    plt.ylabel('Amount (USD)')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    plt.close()
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')