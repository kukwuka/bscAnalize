from .models import AddressInfo
from . import utils


def update_Db():
    soldDfx, boughtDfx = utils.parse_contract_transations(utils.CAKE_LP_ADDRESS, "DFX")
    stack, merge = utils.parse_contract_transations(utils.ST_DFX_ADDRESS, "")
    finite_data = utils.group_4data_by_person(soldDfx, boughtDfx, stack, merge)
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


def buy_sold_graphs_DFX_hash():
    soldDfx, boughtDfx = utils.parse_contract_transations(utils.CAKE_LP_ADDRESS, "DFX")
    soldDfxBusd, boughtDfxBusd = utils.parse_contract_transations(utils.CAKE_LP_ADDRESS, "BUSD")
    result = utils.group_by_time_with_hash(soldDfx, boughtDfx, soldDfxBusd, boughtDfxBusd)

    return result


def yesterday_buy_sold_delta():
    table = buy_sold_graphs_DFX_hash()

    return utils.get_yesterday_delta(table)


def stack_merge_graphs_Stacking():
    merge, stack = utils.parse_contract_transations(utils.ST_DFX_ADDRESS, "")
    result = utils.group_by_time(merge, stack)

    return result


def stack_merge_graphs_Farming():
    merge, stack = utils.parse_contract_transations(utils.FARMING_DFX_ADDRESS, "Cake-LP")
    result = utils.group_by_time(merge, stack)

    return result


def total_supply():
    return utils.total_supply_request()
