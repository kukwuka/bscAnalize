from django.shortcuts import render

from datetime import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt

import io
import base64, urllib


def stampToTime(timestamp: str):
    tsint = int(timestamp)
    return datetime.utcfromtimestamp(tsint).strftime('%Y-%m-%d')


def BoughtGraph(bought):
    plt.figure(figsize=(20, 10))
    plt.switch_backend('AGG')
    buf = io.BytesIO()
    dfBought = pd.DataFrame.from_dict(bought, orient='columns').groupby('timeStamp').sum()
    dfBought.plot(label="покупка", figsize=(20, 5))
    # fig = plt.gcf()

    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    return urllib.parse.quote(string)


def SoldGraph(sold):
    plt.figure(figsize=(20, 10))
    plt.switch_backend('AGG')
    buf = io.BytesIO()
    dfSold = pd.DataFrame.from_dict(sold, orient='columns').groupby('timeStamp').sum()
    dfSold.plot(figsize=(20, 5), color='green')
    # fig = plt.gcf()

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
    respond = requests.get(
        "https://api.bscscan.com/api?module=account&action=tokentx&address=0xe7ff9aceb3767b4514d403d1486b5d7f1b787989&startblock=0&endblock=25000000&sort=asc&apikey=YourApiKeyToken")

    resJson = respond.json()["result"]

    sold = []
    bought = []

    BusdSold = 0
    BusdBought = 0

    for transaction in resJson:
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
    dfBoughtPerson = pd.DataFrame.from_dict(bought, orient='columns').groupby('from').sum().sort_values("value").to_dict('index')
    dfSoldPerson = pd.DataFrame.from_dict(sold, orient='columns').groupby('to').sum().sort_values("value").to_dict('index')

    return render(request, 'index.html', {
        'BoughtGraph': BoughtGraph(bought),
        'SoldGraph': SoldGraph(sold),
        'dfBoughtPerson': dfSoldPerson,
        'dfSoldPerson': dfSoldPerson
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
