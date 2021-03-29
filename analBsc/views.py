from django.db.models.functions import Coalesce
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AddressInfo
from .serializers import AddressInfoSerializer
from .service import (
    update_Db,
    buy_sold_graphs_DFX,
    buy_sold_graphs_BUSD,
    stack_merge_graphs_Stacking,
    stack_merge_graphs_Farming)


def updateCache(request):
    update_Db()
    return JsonResponse({"status": "updated"})


def buy_sold_graphs_DFX_View(request):
    sold, buy = buy_sold_graphs_DFX()
    return JsonResponse({'sold': sold, 'buy': buy}, safe=False)


def buy_sold_graphs_BUSD_View(request):
    buy, sold = buy_sold_graphs_BUSD()
    return JsonResponse({'sold': sold, 'buy': buy}, safe=False)


def stack_merge_graphs_Stacking_View(request):
    merge, stack = stack_merge_graphs_Stacking()
    return JsonResponse({'merge': merge, 'stack': stack}, safe=False)


def stack_merge_graphs_Farming_View(request):
    merge, stack = stack_merge_graphs_Farming()
    return JsonResponse({'merge': merge, 'stack': stack}, safe=False)


class AddressInfoView(APIView):

    def get(self, request):
        adressInfo = AddressInfo.objects.all().order_by(Coalesce(
            'sumOfDfxOfUser',
            'value_buy',
            'value_FromStack').desc())
        serializer = AddressInfoSerializer(adressInfo, many=True)
        return Response(serializer.data)
