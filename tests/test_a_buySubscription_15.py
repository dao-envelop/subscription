import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent. Buy ticket for ether and call agent buySubscription method. With Agent. Ticket is with expiring time 
# and count lefts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent):

	payOptions = [(dai, PRICE, 0), (zero_address, PRICE/5, 0)] #without Agent fee!!!
	subscriptionType = (0,100,0,True, accounts[3]) #time subscription
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter2.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})
	
	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[1][2])/sub_reg.PERCENT_DENOMINATOR()

	before_acc1 = accounts[1].balance()
	before_acc0 = accounts[0].balance()
	before_acc3 = accounts[3].balance()
	before_acc2 = accounts[2].balance()
	before_agent = agent.balance()
	#pay for ether 
	agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert accounts[1].balance() == before_acc1 - pay_amount # payer balance
	assert accounts[0].balance() == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert accounts[3].balance() == before_acc3 + payOptions[1][1] # serviceProvider beneficiary balance
	assert agent.balance() == before_agent #  agent balance was not changed

	minter2.mint(1, {"from": accounts[1]})
	#try to buy subscription again - first subscription is valid
	with reverts("Only one valid ticket at time"):
		agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	#subscription is expired. Buy new time subscription
	#agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	payOptions = [(dai, PRICE, 0), (zero_address, PRICE/5, 0)] #without Agent fee!!!
	subscriptionType = (0,0,1,True, accounts[3])  #count subscription
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter2.authorizeAgentForService(agent.address, [0,1],{"from": accounts[0]})

	with reverts("Only one valid ticket at time"):
		agent.buySubscription(minter2.address, 1, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount}) #try to buy count subscription

	#move time
	chain.sleep(120)
	chain.mine()
	#tariffs is in different order - 0 is tariff with count
	agent.buySubscription(minter2.address, 1, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount}) #try to buy count subscription
	#try to buy count ticket again
	with reverts("Only one valid ticket at time"):
		agent.buySubscription(minter2.address, 1, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount}) #try to buy count subscription
		
	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] ==  1

	minter2.mint(2, {"from": accounts[1]})
	#check - count lefts is changed
	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] ==  0

	#count lefts is 0. Buy new count subscription
	agent.buySubscription(minter2.address, 1, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount}) #try to buy count subscription again.

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] ==  1





