import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

def test_add_tariff(accounts, dai, weth, sub_reg):
    with reverts("Ownable: caller is not the owner"):
        sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[1]})
    sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
    sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

    assert sub_reg.whiteListedForPayments(dai) == True
    assert sub_reg.whiteListedForPayments(weth) == True

    #register severals tarif for service
    payOptions = [(dai, PRICE, 200), (weth, PRICE/5, 200)]
    subscriptionType = (0,0,1,True, accounts[3])
    tariff1 = (subscriptionType, payOptions)
    sub_reg.registerServiceTariff(tariff1,{'from':accounts[1]})
    actual_tariffs = sub_reg.getTariffsForService(accounts[1]);
    assert len(actual_tariffs) == 1
    assert actual_tariffs[0] == tariff1

    payOptions = [(dai, PRICE/4, 200), (weth, PRICE/10, 200)]
    subscriptionType = (0,100,0,True, accounts[3])
    tariff2 = (subscriptionType, payOptions)
    sub_reg.registerServiceTariff(tariff2,{'from':accounts[1]})
    actual_tariffs = sub_reg.getTariffsForService(accounts[1]);

    assert len(actual_tariffs) == 2
    assert actual_tariffs[0] == tariff1
    assert actual_tariffs[1] == tariff2

    payOptions = [(dai, PRICE/3, 200), (weth, PRICE/7, 200)]
    subscriptionType = (0,10,0,True, accounts[4])
    tariff1 = (subscriptionType, payOptions)
    sub_reg.registerServiceTariff(tariff1,{'from':accounts[2]})
    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert len(actual_tariffs) == 1
    assert actual_tariffs[0] == tariff1

    payOptions = [(dai, PRICE/5, 200), (weth, PRICE/8, 200)]
    subscriptionType = (0,0,6,True, accounts[4])
    tariff2 = (subscriptionType, payOptions)
    sub_reg.registerServiceTariff(tariff2,{'from':accounts[2]})
    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert len(actual_tariffs) == 2
    assert actual_tariffs[0] == tariff1
    assert actual_tariffs[1] == tariff2

    #there is not tariff for service. Service is not registered
    with reverts("Index out of range"):
        sub_reg.editServiceTariff(0, 0, 100, 0, True, accounts[6], {"from": accounts[5]})

    #there is not tariff for service. Service is registered
    with reverts("Index out of range"):
        sub_reg.editServiceTariff(4, 0, 100, 0, True, accounts[6], {"from": accounts[2]})

    #edit tariff
    sub_reg.editServiceTariff(0, 0, 100, 0, False, accounts[6], {"from": accounts[2]})

    #check edited tariff
    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tariffs[0][0][0] == 0
    assert actual_tariffs[0][0][1] == 100
    assert actual_tariffs[0][0][2] == 0
    assert actual_tariffs[0][0][3] == False
    assert actual_tariffs[0][0][4] == accounts[6]

    #there is not tariff for service. Service is not registered
    with reverts("Index out of range"):
        sub_reg.addTariffPayOption(0, dai, 100, 0, {"from": accounts[5]})

    #there is not tariff for service. Service is registered
    with reverts("Index out of range"):
        sub_reg.addTariffPayOption(3, dai, 100, 0, {"from": accounts[2]})

    #add pay method in tariff
    sub_reg.addTariffPayOption(0, dai, 100, 0, {"from": accounts[2]})

    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tariffs[0][1][2][0] == dai
    assert actual_tariffs[0][1][2][1] == 100
    assert actual_tariffs[0][1][2][2] == 0

    with reverts("Index out of range"):
        sub_reg.editTariffPayOption(0, 5, weth, 100, 0, {"from": accounts[5]})    
    with reverts("Index out of range"):
        sub_reg.editTariffPayOption(0, 5, weth, 100, 0, {"from": accounts[2]})   
    with reverts("Index out of range"):
        sub_reg.editTariffPayOption(3, 0, weth, 100, 0, {"from": accounts[2]})   

    #edit pay method for tariff
    sub_reg.editTariffPayOption(0, 2, weth, 99, 1, {"from": accounts[2]})    
    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert actual_tariffs[0][1][2][0] == weth
    assert actual_tariffs[0][1][2][1] == 99
    assert actual_tariffs[0][1][2][2] == 1

    #authorize agent. Service provider does not have tariffs
    with reverts("Index out of range"):
        sub_reg.authorizeAgentForService(accounts[9], [10,11], {"from": accounts[5]})

    #authorize agent. Service provider has tariffs but with other indexes
    with reverts("Index out of range"):
        sub_reg.authorizeAgentForService(accounts[9], [10,11], {"from": accounts[2]})

    #one tariff is not available. ServiceProvider registers tariffs for agent
    sub_reg.authorizeAgentForService(accounts[9], [0,1], {"from": accounts[2]})
    agent_tariffs = sub_reg.getAvailableAgentsTariffForService(accounts[9], accounts[2])
    actual_tariffs = sub_reg.getTariffsForService(accounts[2]);
    assert agent_tariffs[0] == actual_tariffs[1]
    assert len(agent_tariffs) == 1

    #change platform owner
    with reverts("Only platform owner"):
        sub_reg.setPlatformOwner(accounts[1], {"from": accounts[1]})

    with reverts("Zero platform fee receiver"):
        sub_reg.setPlatformOwner(zero_address, {"from": accounts[0]})

    sub_reg.setPlatformOwner(accounts[1], {"from": accounts[0]})

    #change PlatformFeePercent
    with reverts("Only platform owner"):
        sub_reg.setPlatformFeePercent(40, {"from": accounts[0]})    
    sub_reg.setPlatformFeePercent(40, {"from": accounts[1]})

