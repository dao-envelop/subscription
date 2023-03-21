import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

# one service provider has two Agents with differetn tariffs - self Agent and separate Agent. Buy ticket by all ways and call agent buySubscription method. With Agent. 
#Ticket is with expiring time and count lefts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, agent, wrapper, wnft721):

	sub_reg.setMainWrapper(wrapper.address, {"from": accounts[0]})
	if (wrapper.lastWNFTId(3)[1] == 0):
		wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})

	payOptions1 = [(dai, PRICE, 200), (zero_address, PRICE/5, 200)] #with Agent fee!!!
	subscriptionType1 = (200,100,0,True, accounts[3]) #time subscription with time lock
	tariff1 = (subscriptionType1, payOptions1)

	#add tokens to whiteList
	tx = sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	assert tx.events['WhitelistPaymentTokenChanged']['asset'] == dai.address
	assert tx.events['WhitelistPaymentTokenChanged']['state'] == True

	sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})

	#register tariffs for service
	tx = minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	assert tx.events['TariffChanged']['service'] == minter1.address
	assert tx.events['TariffChanged']['tariffIndex'] == 0

	payOptions2 = [(dai, PRICE/2, 300), (zero_address, PRICE/10, 300)] #with Agent fee!!!
	subscriptionType2 = (0,100,0,True, accounts[3]) #time subscription with time lock
	tariff2 = (subscriptionType2, payOptions2)

	#register tariffs for service
	minter1.registerServiceTariff(tariff2,{'from':accounts[0]})

	payOptions3 = [(dai, PRICE/2, 400), (zero_address, PRICE/10, 400)] #with Agent fee!!!
	subscriptionType3 = (0,0,1,True, accounts[3]) #time subscription with time lock
	tariff3 = (subscriptionType3, payOptions3)

	#register tariffs for service
	minter1.registerServiceTariff(tariff3,{'from':accounts[0]})


	#register agents
	minter1.authorizeAgentForService(minter1.address, [0,1,2],{"from": accounts[0]}) #self Agent
	minter1.authorizeAgentForService(agent.address, [0,1,2],{"from": accounts[0]}) #separate Agent
	
	pay_amount = payOptions1[0][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions1[0][2])/sub_reg.PERCENT_DENOMINATOR()

	dai.transfer(accounts[1], pay_amount, {"from": accounts[0]})
	dai.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	before_acc1 = dai.balanceOf(accounts[1])
	before_acc0 = dai.balanceOf(accounts[0])
	before_acc3 = dai.balanceOf(accounts[3])
	before_m = dai.balanceOf(minter1)

	#pay by wrapping erc20 - using self Agent, time ticket
	tx = minter1.buySubscription(minter1.address, 0, 0, accounts[1], accounts[1], {"from": accounts[1]})

	assert tx.events['TicketIssued']['service'] == minter1.address
	assert tx.events['TicketIssued']['agent'] == minter1.address
	assert tx.events['TicketIssued']['forUser'] == accounts[1]
	assert tx.events['TicketIssued']['tariffIndex'] == 0

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType1[2]

	#check balance
	assert dai.balanceOf(accounts[1]) == before_acc1 - payOptions1[0][1] # payer balance
	assert dai.balanceOf(accounts[0]) == before_acc0  					# planform beneficiary balance
	assert dai.balanceOf(accounts[3]) == before_acc3  					# serviceProvider beneficiary balance
	assert dai.balanceOf(minter1) == before_m							 #  agent balance 
	assert dai.balanceOf(wrapper) == payOptions1[0][1]					#wrapper balance

	#pay by erc20 tokens, using separate agent

	pay_amount = payOptions2[0][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions2[0][2])/sub_reg.PERCENT_DENOMINATOR()

	dai.transfer(accounts[2], pay_amount, {"from": accounts[0]})
	dai.approve(sub_reg.address, pay_amount, {"from": accounts[2]})
	before_acc0 = dai.balanceOf(accounts[0])
	before_acc3 = dai.balanceOf(accounts[3])
	before_acc2 = dai.balanceOf(accounts[2])
	before_agent = dai.balanceOf(agent)

	assert sub_reg.getTicketPrice(minter1.address, 1,0)[1] == pay_amount

	#buy usins second tariff and second agent - time subscription
	tx = agent.buySubscription(minter1.address, 1, 0, accounts[2], accounts[2], {"from": accounts[2]})

	assert tx.events['TicketIssued']['service'] == minter1.address
	assert tx.events['TicketIssued']['agent'] == agent.address
	assert tx.events['TicketIssued']['forUser'] == accounts[2]
	assert tx.events['TicketIssued']['tariffIndex'] == 1

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[2])
	assert ticket[0] > chain.time()
	assert ticket[1] == 0

	#check balance
	assert dai.balanceOf(accounts[2]) == before_acc2 - pay_amount  		  # payer balance
	assert dai.balanceOf(accounts[0]) == before_acc0 + payOptions2[0][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR()  # planform beneficiary balance
	assert dai.balanceOf(accounts[3]) == before_acc3 + payOptions2[0][1]	  # serviceProvider beneficiary balance
	assert dai.balanceOf(agent) == before_agent + payOptions2[0][1]* payOptions2[0][2]/	sub_reg.PERCENT_DENOMINATOR()	 #  agent balance
	
	###################
	#pay by ether, using separate agent

	pay_amount = payOptions3[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions3[1][2])/sub_reg.PERCENT_DENOMINATOR()

	before_acc0 = accounts[0].balance()
	before_acc3 = accounts[3].balance()
	before_acc4 = accounts[2].balance()
	before_agent = agent.balance()


	#buy usins third tariff and second agent - count subscription
	agent.buySubscription(minter1.address, 2, 1, accounts[4], accounts[4], {"from": accounts[4], "value": pay_amount})

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[4])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 1

	#check balance
	assert accounts[4].balance() == before_acc4 - pay_amount  		  # payer balance
	assert accounts[0].balance() == before_acc0 + payOptions3[1][1]* sub_reg.platformFeePercent()/ sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert accounts[3].balance() == before_acc3 + payOptions3[1][1]	  # serviceProvider beneficiary balance
	assert agent.balance() == before_agent + payOptions3[1][1]* payOptions3[1][2]/	sub_reg.PERCENT_DENOMINATOR()	 #  agent balance


	#using subscriptions
	minter1.mint(1, {"from": accounts[1]})
	minter1.mint(2, {"from": accounts[2]})
	minter1.mint(3, {"from": accounts[4]})

	#check tickets after using subscription
	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[4])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 0

	
	minter1.mint(4, {"from": accounts[1]})
	minter1.mint(5, {"from": accounts[2]})

	assert minter1.checkUserSubscription(accounts[2])[0] == True
	assert minter1.checkUserSubscription(accounts[2])[1] == False

	#buy ticket than switch off tariff
	agent.buySubscription(minter1.address, 2, 1, accounts[5], accounts[5], {"from": accounts[5], "value": pay_amount})

	#switch off tariff
	minter1.editServiceTariff(2,0,0,1, False, accounts[3], {"from": accounts[0]})

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[5])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 1

	'''minter1.fixUserSubscription(accounts[5], {"from": accounts[1]})

	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[5])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 0'''

	minter1.mint(6, {"from": accounts[5]})
	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[5])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 0
	assert minter1.checkUserSubscription(accounts[5])[0] == False
	assert minter1.checkUserSubscription(accounts[5])[1] == False

	#try to buy ticket. Tariff is switched off  
	with reverts("This subscription not available"):
		agent.buySubscription(minter1.address, 2, 1, accounts[4], accounts[4], {"from": accounts[4], "value": pay_amount})
