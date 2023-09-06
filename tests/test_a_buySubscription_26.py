import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket for erc20 tokens and call serviceProvider method. Without Agent. Ticket is with expiring time
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1):

	#checking of subscription is switched on default
	payOptions = [(dai, PRICE, 0), (weth, PRICE/5, 0)] #without Agent fee
	subscriptionType = (0,100,0,True, accounts[3])
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	with reverts("Valid ticket not found"):
		minter1.mint(1, {"from": accounts[1]})

	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent())/sub_reg.PERCENT_DENOMINATOR()
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})
	weth.approve(sub_reg.address, pay_amount-1, {"from": accounts[1]})

	before_acc1 = weth.balanceOf(accounts[1])
	before_acc0 = weth.balanceOf(accounts[0])
	minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})
	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]
	#check balance
	assert weth.balanceOf(accounts[3]) == payOptions[1][1] # balance beneficiary of serviceProvider
	assert weth.balanceOf(accounts[1]) == before_acc1 - pay_amount #balance payer
	assert weth.balanceOf(accounts[0]) == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() #balance platform beneficiary


	minter1.mint(1, {"from": accounts[1]})

	assert minter1.ownerOf(1) == accounts[1]

	#switch off subscription
	with reverts("Ownable: caller is not the owner"):
		minter1.setSubscriptionOnOff(False, {"from": accounts[1]})

	minter1.setSubscriptionOnOff(False, {"from": accounts[0]})

	minter1.mint(2, {"from": accounts[1]})
	assert minter1.ownerOf(2) == accounts[1]

  




