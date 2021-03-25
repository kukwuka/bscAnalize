from django.shortcuts import render

from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

import io
import base64, urllib


def stampToTime(timestamp: str):
    tsint = int(timestamp)
    return datetime.utcfromtimestamp(tsint).strftime('%Y-%m-%d')


def BoughtSoldGraph(bought, sold, ylabel):
    plt.figure(figsize=(20, 10))
    plt.switch_backend('AGG')
    buf = io.BytesIO()
    dfBought = pd.DataFrame.from_dict(bought, orient='columns').groupby('timeStamp').sum()
    dfSold = pd.DataFrame.from_dict(sold, orient='columns').groupby('timeStamp').sum()
    ax = dfBought.plot(figsize=(20, 5))
    dfSold.plot(ax=ax)
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
        .sort_values("value") \
        .to_dict('index')


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
        print(person)
        returndict.append({'address': person[0], 'value': person[1]})

    print(returndict[0])
    return returndict


# Create your views here.
def index(request):
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
    BusdSold = 0
    BusdBought = 0
    for transaction in resJsonSwap:
        transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
        transaction["value"] = (int(transaction["value"])) / 10 ** (18)
        if transaction["tokenSymbol"] == "BUSD":
            if transaction["to"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                bought.append(transaction)
                BusdBought += transaction["value"]
            elif transaction["from"] == "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989":
                sold.append(transaction)
                BusdSold += transaction["value"]
    # Top buyer and seller
    dfBoughtPerson = GruopByPerson(bought,'from')
    dfSoldPerson = GruopByPerson(sold,'to')

    RespondStaking = requests.get(
        "https://api.bscscan.com/api"
        "?module=account&action=tokentx"
        "&address=0x11340dC94E32310FA07CF9ae4cd8924c3cD483fe"
        "&startblock=0"
        "&endblock=25000000"
        "&sort=asc"
        "&apikey=YourApiKeyToken")

    resJsonStaking = RespondStaking.json()["result"]

    stack = []
    merge = []
    ToStack = 0
    FromStack = 0

    for transaction in resJsonStaking:
        transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
        transaction["value"] = (int(transaction["value"])) / 10 ** (18)
        if transaction["to"] == "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe":
            stack.append(transaction)
            ToStack += transaction["value"]
        elif transaction["from"] == "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe":
            merge.append(transaction)
            FromStack += transaction["value"]

    dfStack =  GruopByPerson(stack,'from')
    dfMerge =  GruopByPerson(merge,'to')

    return render(request, 'index.html', {
        'BoughtGraph': BoughtSoldGraph(bought, sold, "Кол-во денях в BUSD"),
        'StackGraph': BoughtSoldGraph(stack, merge, "Кол-во токенов в DFX"),
        'dfBoughtPerson': dfBoughtPerson,
        'dfSoldPerson': dfSoldPerson,
        'dfStack': dfStack,
        'dfMerge': dfMerge,

    })


def home(request):
    plt.plot(range(10))
    fig = plt.gcf()
    # convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    return render(request, 'index.html', {'data': uri})
