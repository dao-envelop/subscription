import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18

def test_add_tariff(accounts, dai, weth, sub_reg):
    with reverts("Ownable: caller is not the owner"):
        sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[1]})
    sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
    sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

    assert sub_reg.whiteListedForPayments(dai) == True
    assert sub_reg.whiteListedForPayments(weth) == True

    payOptions = [(dai, PRICE, 200), (weth, PRICE/5, 200)]
    subscriptionType = (0,0,1,True, accounts[3])
    tarif1 = (subscriptionType, payOptions)
    sub_reg.registerServiceTarif(tarif1,{'from':accounts[1]})
    actual_tarifs = sub_reg.getTariffsForService(accounts[1]);
    assert len(actual_tarifs) == 1
    assert actual_tarifs[0] == tarif1

    payOptions = [(dai, PRICE/4, 200), (weth, PRICE/10, 200)]
    subscriptionType = (0,100,0,True, accounts[3])
    tarif2 = (subscriptionType, payOptions)
    sub_reg.registerServiceTarif(tarif2,{'from':accounts[1]})
    actual_tarifs = sub_reg.getTariffsForService(accounts[1]);

    assert len(actual_tarifs) == 2
    assert actual_tarifs[0] == tarif1
    assert actual_tarifs[1] == tarif2

    payOptions = [(dai, PRICE/3, 200), (weth, PRICE/7, 200)]
    subscriptionType = (0,10,0,True, accounts[4])
    tarif1 = (subscriptionType, payOptions)
    sub_reg.registerServiceTarif(tarif1,{'from':accounts[2]})
    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert len(actual_tarifs) == 1
    assert actual_tarifs[0] == tarif1

    payOptions = [(dai, PRICE/5, 200), (weth, PRICE/8, 200)]
    subscriptionType = (0,0,6,True, accounts[4])
    tarif2 = (subscriptionType, payOptions)
    sub_reg.registerServiceTarif(tarif2,{'from':accounts[2]})
    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert len(actual_tarifs) == 2
    assert actual_tarifs[0] == tarif1
    assert actual_tarifs[1] == tarif2

    #there is not tarif for service. Service is not registered
    with reverts("Index out of range"):
        sub_reg.editServiceTarif(0, 0, 100, 0, True, accounts[6], {"from": accounts[5]})

    #there is not tarif for service. Service is registered
    with reverts("Index out of range"):
        sub_reg.editServiceTarif(4, 0, 100, 0, True, accounts[6], {"from": accounts[2]})

    #edit tarif
    sub_reg.editServiceTarif(0, 0, 100, 0, False, accounts[6], {"from": accounts[2]})

    #check edited tarif
    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tarifs[0][0][0] == 0
    assert actual_tarifs[0][0][1] == 100
    assert actual_tarifs[0][0][2] == 0
    assert actual_tarifs[0][0][3] == False
    assert actual_tarifs[0][0][4] == accounts[6]

    #there is not tarif for service. Service is not registered
    with reverts("Index out of range"):
        sub_reg.addTarifPayOption(0, dai, 100, 0, {"from": accounts[5]})

    #there is not tarif for service. Service is registered
    with reverts("Index out of range"):
        sub_reg.addTarifPayOption(3, dai, 100, 0, {"from": accounts[2]})

    #add pay method
    sub_reg.addTarifPayOption(0, dai, 100, 0, {"from": accounts[2]})

    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tarifs[0][1][2][0] == dai
    assert actual_tarifs[0][1][2][1] == 100
    assert actual_tarifs[0][1][2][2] == 0

    with reverts("Index out of range"):
        sub_reg.editTarifPayOption(0, 5, weth, 100, 0, {"from": accounts[5]})    
    with reverts("Index out of range"):
        sub_reg.editTarifPayOption(0, 5, weth, 100, 0, {"from": accounts[2]})   
    with reverts("Index out of range"):
        sub_reg.editTarifPayOption(3, 0, weth, 100, 0, {"from": accounts[2]})   

    #edit pay method for tarif
    sub_reg.editTarifPayOption(0, 2, weth, 99, 1, {"from": accounts[2]})    
    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tarifs[0][1][2][0] == weth
    assert actual_tarifs[0][1][2][1] == 99
    assert actual_tarifs[0][1][2][2] == 1

    #authorize agent. Service provider does not have tarifs
    with reverts("Index out of range"):
        sub_reg.authorizeAgentForService(accounts[9], [10,11], {"from": accounts[5]})

    #authorize agent. Service provider has tarifs but with other indexes
    with reverts("Index out of range"):
        sub_reg.authorizeAgentForService(accounts[9], [10,11], {"from": accounts[2]})

    #one tarif is not available. ServiceProvider registers tarifs for agent
    sub_reg.authorizeAgentForService(accounts[9], [0,1], {"from": accounts[2]})
    agent_tarifs = sub_reg.getAvailableAgentsTarifForService(accounts[9], accounts[2])
    actual_tarifs = sub_reg.getTariffsForService(accounts[2]);
    assert agent_tarifs[0] == actual_tarifs[1]
    assert len(agent_tarifs) == 1



