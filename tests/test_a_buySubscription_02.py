import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket for ether and call serviceProvider method. Without Agent
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1):

	payOptions = [(dai, PRICE, 0), (zero_address, PRICE/5, 0)] #without Agent fee
	subscriptionType = (0,100,0,True, accounts[3])
	tariff1 = (subscriptionType, payOptions)
	#payOptions = [(dai, PRICE/4, 0), (weth, PRICE/10, 0)] #without Agent fee
	#subscriptionType = (0,100,0,True, accounts[3])

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	#try to mint - serviceProvider is registered. But agent is not added
	
	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent())/sub_reg.PERCENT_DENOMINATOR()

	with reverts("Not enough ether"):
		minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": 1})

	before_acc1 = accounts[1].balance()
	before_acc0 = accounts[0].balance()
	before_acc3 = accounts[3].balance()
	#pay for ether  - #more than necessary
	minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": 2*pay_amount}) #more than necessary

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert accounts[1].balance() == before_acc1 - pay_amount # payer balance
	assert accounts[0].balance() == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert accounts[3].balance() == before_acc0 + payOptions[1][1] # serviceProvider beneficiary balance

	minter1.mint(1, {"from": accounts[1]})

	assert minter1.ownerOf(1) == accounts[1]
  




