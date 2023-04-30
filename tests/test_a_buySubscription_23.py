import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent and selfAgent. A lot of tariffs and one tariff is not added to Agent
#repeat real case
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, EnvelopAgentWithRegistry, TokenMock, wrapper, wnft721):

	agent = accounts[0].deploy(EnvelopAgentWithRegistry)
	niftsy = accounts[0].deploy(TokenMock,"NIFTSY MOCK Token", "NIFTSY")

	payOptions = [(zero_address,  100000000000000, 200), (dai, 10000000000000000, 200), (weth.address, 200000000000000, 200), (niftsy.address, 2000000000000000000,200 )] #with Agent fee
	subscriptionType = (0,0,10,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(niftsy, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  100000000000000, 0), (dai.address, 10000000000000000, 0), (weth.address, 200000000000000, 0), (niftsy.address, 2000000000000000000,0 )] #without Agent fee
	subscriptionType = (0,0,10,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  100000000000000, 0), (dai.address, 10000000000000000, 0), (weth.address, 200000000000000, 0), (niftsy.address, 2000000000000000000,0 )] #without Agent fee
	subscriptionType = (360,2592000,0,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  400000000000000, 0), (dai.address, 30000000000000000, 0), (weth.address, 1000000000000000, 0), (niftsy.address, 10000000000000000000,0 )] #without Agent fee
	subscriptionType = (360,0,10,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  300000000000000, 0), (dai.address, 300000000000000, 0), (weth.address, 700000000000000, 0), (niftsy.address, 8000000000000000000,0 )] #without Agent fee
	subscriptionType = (0,2592000,0,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  3000000000000000, 0), (dai.address, 300000000000000, 0), (weth.address, 7000000000000000, 0), (niftsy.address, 80000000000000000000,0 )] #without Agent fee
	subscriptionType = (0,25920000,0,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  13000000000000000, 0), (dai.address, 1600000000000000000, 0), (weth.address, 17000000000000000, 0), (niftsy.address, 180000000000000000000,0 )] #without Agent fee
	subscriptionType = (0,0,100,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  18000000000000000, 0), (dai.address, 2600000000000000000, 0), (weth.address, 27000000000000000, 0), (niftsy.address, 280000000000000000000,0 )] #without Agent fee
	subscriptionType = (360,0,115,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	payOptions = [(zero_address,  38000000000000000, 0), (dai.address, 4600000000000000000, 0), (weth.address, 57000000000000000, 0), (niftsy.address, 680000000000000000000,0 )] #without Agent fee
	subscriptionType = (360,1296000,0,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})


	#register agent - self service Provider
	minter1.authorizeAgentForService(minter1.address, [1,2,3,4,5,6],{"from": accounts[0]})
	minter1.authorizeAgentForService(agent.address, [1,2,3,4,5,6,7,8],{"from": accounts[0]})

	niftsy.approve(sub_reg.address, 10000000000000000000*100000, {"from": accounts[1]})
	#dai.approve(sub_reg.address, 10000000000000000000*100000, {"from": accounts[1]})
	#weth.approve(sub_reg.address, 10000000000000000000*100000, {"from": accounts[1]})

	niftsy.transfer(accounts[1], 10000000000000000000*100000, {"from": accounts[0]})

	if (wrapper.lastWNFTId(3)[1] == 0):
		wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})

	#set wrapper
	sub_reg.setMainWrapper(wrapper.address, {"from": accounts[0]})

	agent.buySubscription(minter1.address, 3, 3, accounts[2], accounts[1], {"from": accounts[1]})
	logging.info(sub_reg.getTariffsForService(minter1.address))


	