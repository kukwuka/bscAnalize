from .utils import (
    parse_contract_transations,
    group_4data_by_person,
    total_supply_request,
    gruop_by_person,
    ST_DFX_ADDRESS,
    FARMING_DFX_ADDRESS,
    CAKE_LP_ADDRESS)

from .models import AddressInfo


def update_Db():
    soldDfx, boughtDfx = parse_contract_transations(CAKE_LP_ADDRESS, "DFX")
    stack, merge = parse_contract_transations(ST_DFX_ADDRESS, "")
    finite_data = group_4data_by_person(soldDfx, boughtDfx, stack, merge)
    for address in finite_data:
        obj, created = AddressInfo.objects.update_or_create(
            address=address['person'],
            defaults={
                'value_buy': address['value_buy (DFX)'],
                'value_sold': address['value_sold (DFX)'],
                'value_FromStack': address['value_FromStack (DFX)'],
                'value_ToStack': address['value_ToStack (DFX)'],
                'dfxBalance': address['DfxBalance'],
                'stDfxBalance': address['StDfxBalance'],
                'lpFarmingBalance': address['LpFarmingBalance'],
                'userDfxAmountFromStDFX': address['UserDfxAmountFromStDFX'],
                'userDfxAmountFromCakeLP': address['UserDfxAmountFromCakeLP'],
                'sumOfDfxOfUser': address['SumOfDfxOfUser'],
            },
        )


def buy_sold_graphs_DFX():
    soldDfx, boughtDfx = parse_contract_transations(CAKE_LP_ADDRESS, "DFX")
    soldDfxGrouped, boughtDfxGrouped = gruop_by_person(soldDfx, boughtDfx)

    return soldDfxGrouped, boughtDfxGrouped


def buy_sold_graphs_BUSD():
    soldDfx, boughtDfx = parse_contract_transations(CAKE_LP_ADDRESS, "BUSD")
    soldDfxGrouped, boughtDfxGrouped = gruop_by_person(soldDfx, boughtDfx)
    return soldDfxGrouped, boughtDfxGrouped


def stack_merge_graphs_Stacking():
    merge, stack = parse_contract_transations(ST_DFX_ADDRESS, "")
    mergeDfxGrouped, stackDfxGrouped = gruop_by_person(merge, stack)
    return mergeDfxGrouped, stackDfxGrouped


def stack_merge_graphs_Farming():
    merge, stack = parse_contract_transations(FARMING_DFX_ADDRESS, "Cake-LP")
    mergeLpGrouped, stackLpGrouped = gruop_by_person(merge, stack)
    return mergeLpGrouped, stackLpGrouped


def total_supply():
     return total_supply_request()



