from django.shortcuts import render

from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

import io
import base64, urllib
from web3 import Web3

from .abi import abiDfx, abiStDfx, abiFarming, abiCakeLp

ST_DFX_ADDRESS = "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe"
DFX_ADDRESS = "0x74B3abB94e9e1ECc25Bd77d6872949B4a9B2aACF"
FARMING_DFX_ADDRESS = "0x9d943FD36adD58C42568EA1459411b291FF7035F"
CAKE_LP_ADDRESS = "0xE7FF9AcEB3767B4514d403D1486B5D7f1b787989"
WEI = 10 ** 18


def stampToTime(timestamp: str):
    tsint = int(timestamp)
    return datetime.utcfromtimestamp(tsint).strftime('%Y-%m-%d')


def boughtSoldGraph(bought, sold, ylabel, nameBought, nameSold):
    matplotlib.use('Agg')
    plt.figure(figsize=(20, 10))
    buf = io.BytesIO()
    dfBought = pd.DataFrame.from_dict(bought, orient='columns').groupby('timeStamp').sum().rename(
        columns={'value': nameBought})
    dfSold = pd.DataFrame.from_dict(sold, orient='columns').groupby('timeStamp').sum().rename(
        columns={'value': nameSold})
    dates = dfBought.index.values
    BoughtRow = dfBought[nameBought].to_numpy()
    SoldRow = dfSold[nameSold].to_numpy()
    if len(BoughtRow) > len(SoldRow):
        BoughtRow = BoughtRow[0:len(SoldRow)]
        dates = dates[0:len(SoldRow)]
    else:
        SoldRow = SoldRow[0:len(BoughtRow)]
        dates = dates[0:len(BoughtRow)]
    Delta = BoughtRow - SoldRow
    dfDelta = pd.DataFrame(data=Delta, index=dates, columns=["delta"])
    # print(dfSold)

    ax = dfBought.plot(figsize=(20, 5), grid=True, marker='o')
    ax2 = dfSold.plot(ax=ax, grid=True, marker='o')
    dfDelta.plot(ax=ax2, grid=True, marker='o')
    plt.ylabel(ylabel)
    plt.xlabel("Дата")
    plt.savefig(buf, format='png')
    plt.grid(which='minor', alpha=0.2)
    plt.grid(which='major', alpha=0.5)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return urllib.parse.quote(string)


def gruopByPerson(data, PersonColumn: str):
    return pd.DataFrame \
        .from_dict(data, orient='columns') \
        .groupby(PersonColumn) \
        .sum() \
        .sort_values("value", ascending=False) \
        .to_dict('index')


def joinDf(data1, data2, stackData, mergedata):
    # Страемся Группировать, но как-то нихуя не получается, но мы пробьеюмся(нет)
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    df1 = pd.DataFrame.from_dict(data1, orient='columns').groupby('person').sum()
    df2 = pd.DataFrame.from_dict(data2, orient='columns').groupby('person').sum()
    dfStack = pd.DataFrame.from_dict(stackData, orient='columns').set_index('person').groupby('person').sum()
    dfmerge = pd.DataFrame.from_dict(mergedata, orient='columns').set_index('person').groupby('person').sum()
    JoinedDf = df1.join(df2, on='person', how='outer', lsuffix='_buy (DFX)', rsuffix='_sold (DFX)')
    JoinedDf = JoinedDf.join(dfStack, on='person', how='outer', lsuffix='_ToStack (DFX)', rsuffix='Second')
    JoinedDf = JoinedDf.join(dfmerge, on='person', how='outer', lsuffix='_FromStack (DFX) ', rsuffix='_FromStack (DFX)')
    JoinedDf.reset_index(drop=True, inplace=True)
    print(JoinedDf)

    ContractDfx = w3.eth.contract(address=DFX_ADDRESS, abi=abiDfx())
    ContractStDfx = w3.eth.contract(address=Web3.toChecksumAddress(ST_DFX_ADDRESS), abi=abiStDfx())
    ContractFarmingDfx = w3.eth.contract(address=Web3.toChecksumAddress(FARMING_DFX_ADDRESS), abi=abiFarming())
    ContractCekeLpToken = w3.eth.contract(address=Web3.toChecksumAddress(CAKE_LP_ADDRESS), abi=abiCakeLp())

    DFX_BALANCE_OF_STDFX_ON_DFX = float(
        ContractDfx.functions.balanceOf(
            Web3.toChecksumAddress(ST_DFX_ADDRESS)
        ).call() / WEI)
    DFX_BALANCE_OF_CAKE_LP_ON_DFX = float(
        ContractDfx.functions.balanceOf(
            Web3.toChecksumAddress(CAKE_LP_ADDRESS)
        ).call() / WEI)

    STDFX_TOTAL_SUPLY = float(ContractStDfx.functions.totalSupply().call() / WEI)
    CAKE_LP_TOTAL_SUPLY = float(ContractCekeLpToken.functions.totalSupply().call() / WEI)

    DfxBalance = []
    StDfxBalance = []
    LpFarmingBalance = []
    UserDfxAmountFromStDFX = []
    UserDfxAmountFromCakeLP = []
    SumOfDfxOfUser = []
    j = 0
    for i in JoinedDf.to_dict('records'):
        # if j>5 :
        #     LpFarmingBalance.append(0)
        #     DfxBalance.append(0)
        #     StDfxBalance.append(0)
        #     continue
        resIntDfxBalance = ContractDfx.functions.balanceOf(Web3.toChecksumAddress(i['person'])).call()
        DfxBalanceUser = float(resIntDfxBalance / WEI)
        DfxBalance.append(DfxBalanceUser)

        resIntStDfxBalance = ContractStDfx.functions.balanceOf(Web3.toChecksumAddress(i['person'])).call()
        StDfxBalanceOfPerson = float(resIntStDfxBalance / WEI)
        StDfxBalance.append(StDfxBalanceOfPerson)
        UserDfxAmountFromStDFX.append(StDfxBalanceOfPerson * DFX_BALANCE_OF_STDFX_ON_DFX / STDFX_TOTAL_SUPLY)

        resIntFarmingDfxBalance = ContractFarmingDfx.functions.userInfo(1, Web3.toChecksumAddress(i['person'])).call()
        CakeLpBalanceOfPerson = float(resIntFarmingDfxBalance[0] / WEI)
        LpFarmingBalance.append(CakeLpBalanceOfPerson)
        UserDfxAmountFromCakeLP.append(CakeLpBalanceOfPerson * DFX_BALANCE_OF_CAKE_LP_ON_DFX / CAKE_LP_TOTAL_SUPLY)

        SumOfDfxOfUser.append(DfxBalanceUser + StDfxBalanceOfPerson + CakeLpBalanceOfPerson)
        j += 1
        print(j)

    JoinedDf['DfxBalance'] = DfxBalance
    JoinedDf['StDfxBalance'] = StDfxBalance
    JoinedDf['LpFarmingBalance'] = LpFarmingBalance
    JoinedDf['UserDfxAmountFromStDFX'] = UserDfxAmountFromStDFX
    JoinedDf['UserDfxAmountFromCakeLP'] = UserDfxAmountFromCakeLP
    JoinedDf['SumOfDfxOfUser'] = SumOfDfxOfUser
    Sorted = JoinedDf.sort_values(by=[
        'SumOfDfxOfUser',
        'DfxBalance',
        'StDfxBalance',
        'LpFarmingBalance'
    ], ascending=False)
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

    soldDfx = []
    boughtDfx = []
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
        elif transaction["tokenSymbol"] == "DFX":
            if transaction["to"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                soldDfx.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["from"]
                })

            elif transaction["from"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                boughtDfx.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["to"]
                })

    # Top buyer and seller
    dfBoughtPerson = gruopByPerson(bought, 'person')
    dfSoldPerson = gruopByPerson(sold, 'person')

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
            elif transaction["from"] == "0x9d943fd36add58c42568ea1459411b291ff7035f":
                mergeFarming.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["to"]
                })

    dfStack = gruopByPerson(stack, 'person')
    dfMerge = gruopByPerson(merge, 'person')

    return render(request, 'index.html', {
        "Df": joinDf(boughtDfx, soldDfx, stack, merge),
        'FarmingGraph': boughtSoldGraph(stackFarming, mergeFarming, "Кол-во токенов в Cake-LP", "Залили", "Слили"),
        'BoughtGraph': boughtSoldGraph(bought, sold, "Кол-во денях в BUSD", "продали", "купили"),
        'BoughtGraphDfx': boughtSoldGraph(boughtDfx, soldDfx, "Кол-во токенов в DFX", "продали", "купили"),
        'StackGraph': boughtSoldGraph(stack, merge, "Кол-во токенов в DFX", "Слили", "Залили"),

        'dfBoughtPerson': dfBoughtPerson,
        'dfSoldPerson': dfSoldPerson,
        'dfStack': dfStack,
        'dfMerge': dfMerge,

    })




def home(request):
    # w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    # Contract = w3.eth.contract(address="0x74B3abB94e9e1ECc25Bd77d6872949B4a9B2aACF", abi=abi())
    # check = Contract.functions.balanceOf("0x9d943FD36adD58C42568EA1459411b291FF7035F").call()
    return render(request, 'index.html', {'data': "check"})
