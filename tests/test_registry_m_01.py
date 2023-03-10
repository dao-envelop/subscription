import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3




def test_add_tariff(accounts, dai, sub_reg):
    sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
    assert sub_reg.whiteListedForPayments(dai) == True
    payOptions = [(dai, 1e18, 200),]
    subscriptionType = (0,0,1,True, accounts[3])
    tarif = (subscriptionType, payOptions)
    sub_reg.registerServiceTarif(tarif,{'from':accounts[1]})
    actual_tarifs = sub_reg.getTariffsForService(accounts[1]);
    logging.info(
        'Service:({}),'
        '\ntarifs = {}'.format(
            accounts[1],
            actual_tarifs
    ))
    assert len(actual_tarifs) == 1


    # [treeMock.insertKeyValue(KEYS_0[0], x, {"from": accounts[0]}) for x in PRICES_1]
    # assert treeMock.valueKeyCount() == 6
    # assert treeMock.medianValue() == PRICES_1[2]
    # logging.info('Median after PRICES_1 insert:{}'.format(treeMock.medianValue()))
    # for i in PRICES_1:
    #     logging.info(
    #     'Node({:5d}):parent = {:6d}, left = {:6d}, right = {:6d}, isRed = {:<}, keyCount = {:3d}, count = {:3d}'.format(
    #         i,
    #         treeMock.getNode2(i)[0],
    #         treeMock.getNode2(i)[1],
    #         treeMock.getNode2(i)[2],
    #         treeMock.getNode2(i)[3],
    #         treeMock.getNode2(i)[4],
    #         treeMock.getNode2(i)[5],
    # ))
    # with reverts("OrderStatisticsTree(403) - Value does not exist."):
    #     treeMock.getNode2(777777777)

