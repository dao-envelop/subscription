import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket by wrapping erc20 tokens and call serviceProvider method. Without Agent. Ticket is with counts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, wrapperTrustedV1, wnft721):

	#set wrapper
	sub_reg.setMainWrapper(wrapperTrustedV1.address, {"from": accounts[0]})

	payOptions = [(dai, PRICE, 0), (weth, PRICE/5, 0)] #without Agent fee
	subscriptionType = (200,0,1,True, zero_address) #without service Provider
	tariff1 = (subscriptionType, payOptions)
	
	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	if (wrapperTrustedV1.lastWNFTId(3)[1] == 0):
		wrapperTrustedV1.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapperTrustedV1.address, {"from": accounts[0]})
	
	pay_amount = payOptions[1][1]

	pay_amount = payOptions[1][1]
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})

	before_acc1 = weth.balanceOf(accounts[1])
	before_w = weth.balanceOf(wrapperTrustedV1.address)

	tx = minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})

	minter1.mint(1, {"from": accounts[1]})
	#counts ran out
	with reverts("Valid ticket not found"):
		minter1.mint(2, {"from": accounts[1]})
	