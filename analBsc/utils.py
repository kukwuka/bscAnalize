from datetime import datetime
import pandas as pd
import requests
from web3 import Web3

from .abi import abiDfx, abiStDfx, abiFarming, abiCakeLp

WEI = 10 ** 18
ST_DFX_ADDRESS = "0x11340dc94e32310fa07cf9ae4cd8924c3cd483fe"
DFX_ADDRESS = "0x74b3abb94e9e1ecc25bd77d6872949b4a9b2aacf"
FARMING_DFX_ADDRESS = "0x9d943fd36add58c42568ea1459411b291ff7035f"
CAKE_LP_ADDRESS = "0xe7ff9aceb3767b4514d403d1486b5d7f1b787989"


def stampToTime(timestamp: str):
    tsint = int(timestamp)
    return datetime.utcfromtimestamp(tsint).strftime('%Y-%m-%d')


def group_dataframe(data, sort_column):
    return pd.DataFrame.from_dict(data, orient='columns').groupby(sort_column).sum()


def parse_contract_transations(account_address: str, token_symbol):
    RespondSwap = requests.get(
        "https://api.bscscan.com/api?"
        "module=account"
        "&action=tokentx"
        f"&address={account_address}"
        "&startblock=0"
        "&endblock=25000000"
        "&sort=asc"
        "&apikey=YourApiKeyToken")
    resJsonSwap = RespondSwap.json()["result"]

    ToUs = []
    FromUs = []

    for transaction in resJsonSwap:

        if (transaction["tokenSymbol"] == token_symbol) or (token_symbol == ""):
            transaction["timeStamp"] = stampToTime(transaction["timeStamp"])
            transaction["value"] = (int(transaction["value"])) / WEI
            if transaction["to"] == account_address:
                ToUs.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["from"]
                })
            elif transaction["from"] == account_address:
                FromUs.append({
                    "timeStamp": transaction["timeStamp"],
                    "value": transaction["value"],
                    "person": transaction["to"]
                })
    return ToUs, FromUs


def group_4data_by_person(data1, data2, stackdata, mergedata):
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    df1 = group_dataframe(data1, 'person')
    df2 = group_dataframe(data2, 'person')
    dfStack = group_dataframe(stackdata, 'person')
    dfMerge = group_dataframe(mergedata, 'person')
    JoinedDf = df1.join(
        df2,
        on='person',
        how='outer',
        lsuffix='_buy (DFX)',
        rsuffix='_sold (DFX)')
    JoinedDf = JoinedDf.join(
        dfStack,
        on='person',
        how='outer',
        lsuffix='_ToStack (DFX)',
        rsuffix='Second')
    JoinedDf = JoinedDf.join(
        dfMerge,
        on='person',
        how='outer',
        lsuffix='_FromStack (DFX)',
        rsuffix='_ToStack (DFX)')
    JoinedDf.reset_index(drop=True, inplace=True)

    ContractDfx = w3.eth.contract(address=Web3.toChecksumAddress(DFX_ADDRESS), abi=abiDfx())
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
        # if j > 5:
        #     LpFarmingBalance.append(0)
        #     DfxBalance.append(0)
        #     StDfxBalance.append(0)
        #     UserDfxAmountFromStDFX.append(0)
        #     UserDfxAmountFromCakeLP.append(0)
        #     SumOfDfxOfUser.append(0)
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
    return JoinedDf.fillna(0).to_dict('records')


def gruop_by_person(toData, fromData):
    toDataGroped = pd.DataFrame.from_dict(toData, orient='columns').groupby('timeStamp').sum()
    fromDataGroped = pd.DataFrame.from_dict(fromData, orient='columns').groupby('timeStamp').sum()

    return toDataGroped.to_dict(), fromDataGroped.to_dict()


def total_supply_request():
    RespondSwap = requests.get(
        "https://api.bscscan.com/api?"
        "module=stats&action=tokensupply"
        "&contractaddress=0x74b3abb94e9e1ecc25bd77d6872949b4a9b2aacf"
        "&apikey=X7UE235AN5BWK43SPCUPG2DZAQPZ9BPG46"
    )
    return RespondSwap.json()["result"]
