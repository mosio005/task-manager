from django_filters import FilterSet, filters, BaseInFilter, CharFilter, BooleanFilter

from .models import Task


class CharInFilter(
    BaseInFilter,
    CharFilter
):
    pass



class TaskFilter(FilterSet):

    status = CharInFilter(
        field_name='status',
        lookup_expr='in'
    )

    is_expired = BooleanFilter(
        field_name='is_expired',
    )


    class Meta:
        model = Task   
        fields = ['priority']