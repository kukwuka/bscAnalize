import hashlib
import random
import string

from django.http import JsonResponse
from django.shortcuts import render

from .service import (
    update_Db,
    yesterday_buy_sold_delta,
    buy_sold_graphs_DFX_hash,
    stack_merge_graphs_Stacking,
    stack_merge_graphs_Farming,
    total_supply,
)


def updateCache(request):
    update_Db()
    return JsonResponse({"status": "updated"})


def check_hash(request):
    result = buy_sold_graphs_DFX_hash()
    return JsonResponse(result, safe=False)


def yesterday_delta(request):
    return JsonResponse({'yesterday_buy_sell_delta_DFX': yesterday_buy_sold_delta()}, safe=False)


def stack_merge_graphs_Stacking_View(request):
    return JsonResponse({'stack_merge_StDfx': stack_merge_graphs_Stacking()}, safe=False)


def stack_merge_graphs_Farming_View(request):
    return JsonResponse({'stack_merge_CakeLp': stack_merge_graphs_Farming()}, safe=False)


def total_supply_View(request):
    return JsonResponse({'total_supply': total_supply()}, safe=False)


def index_html(request):
    return render(request, 'main.html')


def send_messages(request):
    pool = string.ascii_letters + string.digits
    random_string = (''.join(random.choice(pool) for _ in range(256))).encode('utf-8')
    hash_object = hashlib.sha256(random_string)
    hex_dig = hash_object.hexdigest()
    return JsonResponse({'total_supply': hex_dig}, safe=False)
