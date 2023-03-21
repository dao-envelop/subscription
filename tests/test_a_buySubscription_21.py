import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

# one service provider has two Agents with differetn tariffs - self Agent and separate Agent. Buy ticket for wrapping erc20 and call agent buySubscription method. With Agent. 
#Ticket is with expiring time and count lefts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, agent, wrapper, wnft721):

	sub_reg.setMainWrapper(wrapper.address, {"from": accounts[0]})
	if (wrapper.lastWNFTId(3)[1] == 0):
		wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})

	payOptions = [(dai, PRICE, 200), (zero_address, PRICE/5, 200)] #with Agent fee!!!
	subscriptionType = (200,100,0,True, accounts[3]) #time subscription with time lock
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]}) #self Agent
	
	pay_amount = payOptions[0][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[0][2])/sub_reg.PERCENT_DENOMINATOR()

	dai.transfer(accounts[1], pay_amount, {"from": accounts[0]})
	dai.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	before_acc1 = dai.balanceOf(accounts[1])
	before_acc0 = dai.balanceOf(accounts[0])
	before_acc3 = dai.balanceOf(accounts[3])
	before_m = dai.balanceOf(minter1)
	#pay by wrapping erc20 tokens
	minter1.buySubscription(minter1.address, 0, 0, accounts[1], accounts[1], {"from": accounts[1]})

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert dai.balanceOf(accounts[1]) == before_acc1 - payOptions[0][1] # payer balance
	assert dai.balanceOf(accounts[0]) == before_acc0  					# planform beneficiary balance
	assert dai.balanceOf(accounts[3]) == before_acc3  					# serviceProvider beneficiary balance
	assert dai.balanceOf(minter1) == before_m							 #  agent balance 
	assert dai.balanceOf(wrapper) == payOptions[0][1]					#wrapper balance

	#####registry second agent

	payOptions = [(dai, PRICE*2, 200), (zero_address, PRICE/2, 200)] #with Agent fee!!!
	subscriptionType = (300,0,1,True, accounts[3]) #count subscription with time lock
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter1.authorizeAgentForService(agent.address, [1],{"from": accounts[0]}) #separate Agent
	
	pay_amount = payOptions[0][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[0][2])/sub_reg.PERCENT_DENOMINATOR()

	dai.transfer(accounts[2], pay_amount, {"from": accounts[0]})
	dai.approve(sub_reg.address, pay_amount, {"from": accounts[2]})
	before_acc0 = dai.balanceOf(accounts[0])
	before_acc3 = dai.balanceOf(accounts[3])
	before_acc2 = dai.balanceOf(accounts[2])
	before_agent = dai.balanceOf(agent)
	before_w = dai.balanceOf(wrapper)

	assert sub_reg.getTicketPrice(minter1.address, 1,0)[1] == payOptions[0][1]

	#pay for ether 
	with reverts("Only one valid ticket at time"):
		agent.buySubscription(minter1.address, 1, 1, accounts[1], accounts[1], {"from": accounts[1]})

	#buy usins second tariff and second agent - count subscription
	agent.buySubscription(minter1.address, 1, 0, accounts[2], accounts[2], {"from": accounts[2]})

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[2])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 1

	#check balance
	assert dai.balanceOf(accounts[2]) == before_acc2 - payOptions[0][1] # payer balance
	assert dai.balanceOf(accounts[0]) == before_acc0 					 # planform beneficiary balance
	assert dai.balanceOf(accounts[3]) == before_acc3 					# serviceProvider beneficiary balance
	assert dai.balanceOf(agent) == before_agent 						 #  agent balance
	assert dai.balanceOf(wrapper) == before_w + payOptions[0][1]		#wrapper balance

	#using subscriptions
	minter1.mint(1, {"from": accounts[1]})
	minter1.mint(2, {"from": accounts[2]})

	#check tickets after using subscription
	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[2])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 0

	with reverts("Valid ticket not found"):
		minter1.mint(3, {"from": accounts[2]})
	minter1.mint(3, {"from": accounts[1]})

