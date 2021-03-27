from django.shortcuts import render

from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

import io
import base64, urllib
from web3 import Web3

from .abi import abiDfx, abiStDfx, abiFarming

ST_DFX_ADDRESS = "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe"
DFX_ADDRESS = "0x74B3abB94e9e1ECc25Bd77d6872949B4a9B2aACF"
FARMING_DFX_ADDRESS = "0x9d943FD36adD58C42568EA1459411b291FF7035F"
WEI = 10 ** 18


def stampToTime(timestamp: str):
    tsint = int(timestamp)
    return datetime.utcfromtimestamp(tsint).strftime('%Y-%m-%d')


def BoughtSoldGraph(bought, sold, ylabel):
    matplotlib.use('Agg')
    plt.figure(figsize=(20, 10))
    buf = io.BytesIO()
    dfBought = pd.DataFrame.from_dict(bought, orient='columns').groupby('timeStamp').sum().interpolate(method='linear')
    dfSold = pd.DataFrame.from_dict(sold, orient='columns').groupby('timeStamp').sum().interpolate(method='linear')
    ax = dfBought.plot(figsize=(20, 5), grid=True)
    dfSold.plot(ax=ax, grid=True, )
    plt.ylabel(ylabel)
    plt.xlabel("Дата")
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return urllib.parse.quote(string)


def GruopByPerson(data, PersonColumn: str):
    return pd.DataFrame \
        .from_dict(data, orient='columns') \
        .groupby(PersonColumn) \
        .sum() \
        .sort_values("value", ascending=False) \
        .to_dict('index')


def joinDf(data1, data2):
    # Страемся Группировать, но как-то нихуя не получается, но мы пробьеюмся(нет)
    w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    df1 = pd.DataFrame.from_dict(data1, orient='columns').set_index('person').groupby('person').sum()
    df2 = pd.DataFrame.from_dict(data2, orient='columns').set_index('person').groupby('person').sum()
    JoinedDf = df1.join(df2, on='person', how='outer', lsuffix='_buy (BUSD)', rsuffix='_sold (BUSD)')
    JoinedDf.reset_index(drop=True, inplace=True)

    ContractDfx = w3.eth.contract(address=DFX_ADDRESS, abi=abiDfx())
    ContractStDfx = w3.eth.contract(address=Web3.toChecksumAddress(ST_DFX_ADDRESS), abi=abiStDfx())
    ContractFarmingDfx = w3.eth.contract(address=Web3.toChecksumAddress(FARMING_DFX_ADDRESS), abi=abiFarming())

    DFX_BALANCE_OF_STDFX_ON_DFX = float(
        ContractDfx.functions.balanceOf(
            Web3.toChecksumAddress(ST_DFX_ADDRESS)
        ).call() / WEI)

    STDFX_TOTAL_SUPLY = float(ContractStDfx.functions.totalSupply().call() / WEI)

    DfxBalance = []
    StDfxBalance = []
    LpFarmingBalance = []
    UserDfxAmountFromStDFX = []
    j = 0
    for i in JoinedDf.to_dict('records'):
        # if j>5 :
        #     LpFarmingBalance.append(0)
        #     DfxBalance.append(0)
        #     StDfxBalance.append(0)
        #     continue
        resIntDfxBalance = ContractDfx.functions.balanceOf(Web3.toChecksumAddress(i['person'])).call()
        DfxBalance.append(float(resIntDfxBalance / WEI))

        resIntStDfxBalance = ContractStDfx.functions.balanceOf(Web3.toChecksumAddress(i['person'])).call()
        StDfxBalanceOfPerson = float(resIntStDfxBalance / WEI)
        StDfxBalance.append(StDfxBalanceOfPerson)
        UserDfxAmountFromStDFX.append(StDfxBalanceOfPerson * DFX_BALANCE_OF_STDFX_ON_DFX / STDFX_TOTAL_SUPLY)

        resIntFarmingDfxBalance = ContractFarmingDfx.functions.userInfo(1, Web3.toChecksumAddress(i['person'])).call()
        LpFarmingBalance.append(float(resIntFarmingDfxBalance[0] / WEI))
        j += 1
        print(j)

        # RespondLpDfxBalance = requests.get(
        #     "https://api.bscscan.com/api?module=account"
        #     "&action=tokenbalance"
        #     "&contractaddress=0xe7ff9aceb3767b4514d403d1486b5d7f1b787989"
        #     f"&address={i['person']}"
        #     "&tag=latest&apikey=YourApiKeyToken")
        # resIntLpDfxBalance = int(RespondLpDfxBalance.json()["result"])
        # LpDfxBalance.append(resIntLpDfxBalance / 10 ** 18)

    JoinedDf['DfxBalance'] = DfxBalance
    JoinedDf['StDfxBalance'] = StDfxBalance
    JoinedDf['LpFarmingBalance'] = LpFarmingBalance
    JoinedDf['UserDfxAmountFromStDFX'] = UserDfxAmountFromStDFX
    Sorted = JoinedDf.sort_values(by=['DfxBalance', 'StDfxBalance', 'LpFarmingBalance'], ascending=False)
    # JoinedDf['LpDfxBalance'] = LpDfxBalance

    return Sorted.to_html()


def SoldGraph(sold):
    plt.figure(figsize=(20, 10))
    matplotlib.use('Agg')
    buf = io.BytesIO()
    dfSold = pd.DataFrame.from_dict(sold, orient='columns').groupby('timeStamp').sum()
    dfSold.plot(figsize=(20, 5), color='green')
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return urllib.parse.quote(string)


def dfGeneratorTodict(dfSoldPerson):
    returndict = []
    for person in dfSoldPerson:
        returndict.append({'address': person[0], 'value': person[1]})

    return returndict


# Create your views here.
def index(request):
    # Swap ___________________
    RespondSwap = requests.get(
        "https://api.bscscan.com/api?"
        "module=account"
        "&action=tokentx"
        "&address=0xe7ff9aceb3767b4514d403d1486b5d7f1b787989"
        "&startblock=0"
        "&endblock=25000000"
        "&sort=asc"
        "&apikey=YourApiKeyToken")
    resJsonSwap = RespondSwap.json()["result"]
    sold = []
    bought = []
    for transaction in resJsonSwap:
        transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
        transaction["value"] = (int(transaction["value"])) / 10 ** (18)
        if transaction["tokenSymbol"] == "BUSD":
            if transaction["to"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                bought.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["from"]
                })

            elif transaction["from"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                sold.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["to"]
                })

    # Top buyer and seller
    dfBoughtPerson = GruopByPerson(bought, 'person')
    dfSoldPerson = GruopByPerson(sold, 'person')

    RespondStaking = requests.get(
        "https://api.bscscan.com/api"
        "?module=account&action=tokentx"
        "&address=0x11340dC94E32310FA07CF9ae4cd8924c3cD483fe"
        "&startblock=0"
        "&endblock=25000000"
        "&sort=asc"
        "&apikey=YourApiKeyToken")

    # Stacking ______________
    resJsonStaking = RespondStaking.json()["result"]

    stack = []
    merge = []

    for transaction in resJsonStaking:
        transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
        transaction["value"] = (int(transaction["value"])) / 10 ** (18)
        if transaction["to"] == "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe":
            stack.append({
                "timeStamp": transaction["timeStamp"],
                "value": transaction["value"],
                "person": transaction["from"]
            })
        elif transaction["from"] == "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe":
            merge.append({
                "timeStamp": transaction["timeStamp"],
                "value": transaction["value"],
                "person": transaction["to"]
            })
    # Farming ____________________________________

    RespondFarming = requests.get(
        "https://api.bscscan.com/api?"
        "module=account&action=tokentx"
        "&address=0x9d943FD36adD58C42568EA1459411b291FF7035F"
        "&startblock=0"
        "&endblock=25000000&sort=asc"
        "&apikey=YourApiKeyToken")

    resJsonFarming = RespondFarming.json()["result"]

    stackFarming = []
    mergeFarming = []

    for transaction in resJsonFarming:
        if transaction["tokenSymbol"] == "Cake-LP":
            transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
            transaction["value"] = (int(transaction["value"])) / 10 ** (18)
            if transaction["to"] == "0x9d943fd36add58c42568ea1459411b291ff7035f":
                stackFarming.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["from"]
                })
                print("to")
            elif transaction["from"] == "0x9d943fd36add58c42568ea1459411b291ff7035f":
                mergeFarming.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["to"]
                })
                print("from")

    dfStack = GruopByPerson(stack, 'person')
    dfMerge = GruopByPerson(merge, 'person')
    print(stackFarming)

    return render(request, 'index.html', {
        "Df": joinDf(bought, sold),
        'FarmingGraph': BoughtSoldGraph(stackFarming, mergeFarming, "Кол-во токенов в Cake-LP"),
        'BoughtGraph': BoughtSoldGraph(bought, sold, "Кол-во денях в BUSD"),
        'StackGraph': BoughtSoldGraph(stack, merge, "Кол-во токенов в DFX"),
        'dfBoughtPerson': dfBoughtPerson,
        'dfSoldPerson': dfSoldPerson,
        'dfStack': dfStack,
        'dfMerge': dfMerge,

    })


def home(request):
    w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    Contract = w3.eth.contract(address="0x74B3abB94e9e1ECc25Bd77d6872949B4a9B2aACF", abi=abi())
    check = Contract.functions.balanceOf("0x9d943FD36adD58C42568EA1459411b291FF7035F").call()
    print(check)
    return render(request, 'index.html', {'data': check})
