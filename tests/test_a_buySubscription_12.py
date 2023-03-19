import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent. Buy ticket by wrapping erc20 tokens and call serviceProvider method.
#there is agent fee
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent, wrapper, wnft721):

	#set wrapper
	sub_reg.setMainWrapper(wrapper.address, {"from": accounts[0]})

	payOptions = [(dai, PRICE, 100), (weth, PRICE/5, 100)] #with Agent fee
	subscriptionType = (200,100,0,True, accounts[9]) #with service Provider beneficiary - special case
	tariff1 = (subscriptionType, payOptions)
	
	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter2.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})

	if (wrapper.lastWNFTId(3)[1] == 0):
		wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})
	
	pay_amount = payOptions[1][1]
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})

	before_acc1 = weth.balanceOf(accounts[1])
	before_acc0 = weth.balanceOf(accounts[0])
	before_w = weth.balanceOf(wrapper)

	tx = agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})

	assert wnft721.balanceOf(agent.address) == 0
	assert wnft721.balanceOf(accounts[9]) == 0 
	assert wnft721.balanceOf(accounts[0]) == 0

	assert weth.balanceOf(agent.address) == 0  #check agent balance
	assert weth.balanceOf(accounts[9]) == 0 #check service prodier beneficiary balance
	assert before_acc0 == weth.balanceOf(accounts[0])  #check platform owner balance
	assert weth.balanceOf(wrapper) == before_w + pay_amount #check wrapper balance

