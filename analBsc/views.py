from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from . import service
from . import serializers
from .models import Profile, Admin


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def updateCache(request):
    service.update_Db()
    return JsonResponse({"status": "updated"})


@permission_classes((IsAuthenticated,))
def check_hash(request):
    result = service.buy_sold_graphs_DFX_hash()
    return JsonResponse(result, safe=False)


@permission_classes((IsAuthenticated,))
def yesterday_delta(request):
    return JsonResponse({'yesterday_buy_sell_delta_DFX': service.yesterday_buy_sold_delta()}, safe=False)


@permission_classes((IsAuthenticated,))
def stack_merge_graphs_Stacking_View(request):
    return JsonResponse({'stack_merge_StDfx': service.stack_merge_graphs_Stacking()}, safe=False)


@permission_classes((IsAuthenticated,))
def stack_merge_graphs_Farming_View(request):
    return JsonResponse({'stack_merge_CakeLp': service.stack_merge_graphs_Farming()}, safe=False)


@permission_classes((IsAuthenticated,))
def total_supply_View(request):
    return JsonResponse({'total_supply': service.total_supply()}, safe=False)


@permission_classes((IsAuthenticated,))
def index_html(request):
    return render(request, 'main.html')


@permission_classes((IsAuthenticated,))
def profile_dfx_transactions(request, pk):
    try:
        profile = Profile.objects.get(id=pk)

    except ObjectDoesNotExist:
        return JsonResponse({'err': 'profile doesnt exist'}, status=400)

    sold, buy = service.buy_sold_by_person_DFX_hash(profile.blockchain_address)
    balance = service.get_user_balance(profile.blockchain_address)

    return JsonResponse({'sold': sold, 'buy': buy, 'balance': balance}, safe=False)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def admin_info(request):
    user = request.user
    serializer = serializers.UserDetailSerializer(user)
    return Response(serializer.data)


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def admin_info(request):
    user = request.user
    serializer = serializers.UserDetailSerializer(user)
    return Response(serializer.data)


@api_view(['POST', ])
@permission_classes((IsAuthenticated,))
def change_tg_user_name(request):
    try:
        new_tg_username = request.data['new_tg_username']
    except KeyError:
        return Response(status=400)

    admin = Admin.objects.get_or_create(user=request.user)[0]
    # print(admin)
    admin.user_name = new_tg_username
    admin.save()
    return Response(status=200)
