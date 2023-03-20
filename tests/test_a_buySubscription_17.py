import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

# two service providers have different Agents. Buy ticket for ether and call agent buySubscription method. With Agent. Ticket is with expiring time 
# and count lefts
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent, MinterServiceWithAgent, AgentForService):

	payOptions = [(dai, PRICE, 100), (zero_address, PRICE/5, 100)] #with Agent fee!!!
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
	assert agent.balance() == before_agent + payOptions[1][1]*payOptions[1][2]/sub_reg.PERCENT_DENOMINATOR() #  agent balance 

	#####deploy second service provider and agent
	minter2_1 = accounts[0].deploy(MinterServiceWithAgent, sub_reg, "Minter with Agent", 'MWA3')
	agent_1 = accounts[0].deploy(AgentForService)

	payOptions = [(dai, PRICE*2, 200), (zero_address, PRICE/2, 200)] #with Agent fee!!!
	subscriptionType = (0,0,1,True, accounts[3]) #count subscription
	tariff1 = (subscriptionType, payOptions)

	#register tariffs for service
	minter2_1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - separate agent
	minter2_1.authorizeAgentForService(agent_1.address, [0],{"from": accounts[0]})
	
	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[1][2])/sub_reg.PERCENT_DENOMINATOR()

	before_acc1 = accounts[1].balance()
	before_acc0 = accounts[0].balance()
	before_acc3 = accounts[3].balance()
	before_acc2 = accounts[2].balance()
	before_agent_1 = agent_1.balance()

	assert sub_reg.getTicketPrice(minter2_1.address, 0,1)[1] == pay_amount

	#pay for ether 
	agent_1.buySubscription(minter2_1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	ticket = sub_reg.getUserTicketForService(minter2_1.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 1

	#check balance
	assert accounts[1].balance() == before_acc1 - pay_amount # payer balance
	assert accounts[0].balance() == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert accounts[3].balance() == before_acc3 + payOptions[1][1] # serviceProvider beneficiary balance
	assert agent_1.balance() == before_agent_1 + payOptions[1][1]*payOptions[1][2]/sub_reg.PERCENT_DENOMINATOR() #  agent balance

	#using subscriptions
	minter2.mint(1, {"from": accounts[1]})
	minter2_1.mint(1, {"from": accounts[1]})

	#check tickets after using subscription
	ticket = sub_reg.getUserTicketForService(minter2_1.address, accounts[1])
	assert ticket[0] <= chain.time()
	assert ticket[1] == 0

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] > chain.time()
	assert ticket[1] == 0

	minter2.mint(2, {"from": accounts[1]})
	with reverts("Valid ticket not found"):
		minter2_1.mint(2, {"from": accounts[1]})

