import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket for ether and call serviceProvider method. Without Agent. Ticket is with counts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, wrapperTrustedV1, wnft721):

	payOptions = [(dai, PRICE, 0), (zero_address, PRICE/5, 0)] #without Agent fee
	subscriptionType = (0,0,1,True, zero_address) #without service Provider
	tariff1 = (subscriptionType, payOptions)
	
	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent())/sub_reg.PERCENT_DENOMINATOR()

	minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[2], {"from": accounts[1], "value": pay_amount})

	minter1.mint(1, {"from": accounts[1]})
	#counts ran out
	with reverts("Valid ticket not found"):
		minter1.mint(2, {"from": accounts[1]})