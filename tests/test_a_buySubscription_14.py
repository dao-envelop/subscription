import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent. Buy ticket for ether and call agent buySubscription method. With Agent. Ticket is with expiring time
#then subscription registry is being changed. Try to use old ticket
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent, SubscriptionRegistry):

	payOptions = [(dai, PRICE, 100), (zero_address, PRICE/5, 100)] #with Agent fee!!!
	subscriptionType = (0,100,0,True, accounts[3]) #time subscription
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter2.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})
	
	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[1][2])/sub_reg.PERCENT_DENOMINATOR()

	#pay for ether 
	agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	
	########## change subscription registry ########
	sub_reg_new = accounts[0].deploy(SubscriptionRegistry, accounts[0].address)
	with reverts("Ownable: caller is not the owner"):
		sub_reg_new.setPreviousRegistry(sub_reg.address, {"from": accounts[1]})
	sub_reg_new.setPreviousRegistry(sub_reg.address, {"from": accounts[0]})

	with reverts("Ownable: caller is not the owner"):
		sub_reg.setProxyRegistry(sub_reg_new.address, {"from": accounts[1]})
	sub_reg.setProxyRegistry(sub_reg_new.address, {"from": accounts[0]})

	with reverts("Ownable: caller is not the owner"):
		minter2.changeSubscriptionRegistry(sub_reg_new.address, {"from": accounts[1]})
	minter2.changeSubscriptionRegistry(sub_reg_new.address, {"from": accounts[0]})

	#subscription registry is new but user uses ticket of old subscription
	minter2.mint(1, {"from": accounts[1]})
	#try to buy subscription - new subscription registry, there are not registered tariffs in new subscription registry
	with reverts("Index out of range"):
		agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	payOptions = [(dai, PRICE/7, 100), (zero_address, PRICE/15, 100)] #with Agent fee!!!
	subscriptionType = (0,0,3,True, accounts[3])  #count subscription
	tariff1 = (subscriptionType, payOptions)
	#add tokens to whiteList
	sub_reg_new.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg_new.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter2.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})

	#subscription is expired. Buy new count subscription
	pay_amount = payOptions[1][1]*(sub_reg_new.PERCENT_DENOMINATOR()+sub_reg_new.platformFeePercent() + payOptions[1][2])/sub_reg_new.PERCENT_DENOMINATOR()
	agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	ticket = sub_reg_new.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] == subscriptionType[2]



