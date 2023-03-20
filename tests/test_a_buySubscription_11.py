import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent. Buy ticket for ether and call agent buySubscription method. With Agent. Ticket is with expiring time
#payer is not same like msg.sender in time of buying subscription
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent):

	payOptions = [(dai, PRICE, 100), (zero_address, PRICE/5, 100)] #with Agent fee
	subscriptionType = (0,100,0,True, accounts[3])
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
	#pay for ether  - #more than necessary
	agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[2], {"from": accounts[1], "value": 2*pay_amount}) #more than necessary

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert accounts[1].balance() == before_acc1 - pay_amount # payer balance
	assert accounts[0].balance() == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert accounts[3].balance() == before_acc3 + payOptions[1][1] # serviceProvider beneficiary balance
	assert accounts[2].balance() == before_acc2 #check payer balance
	assert agent.balance() == before_agent + payOptions[1][1]*payOptions[1][2]/sub_reg.PERCENT_DENOMINATOR() #  agent balance

	minter2.mint(1, {"from": accounts[1]})
	with reverts("Valid ticket not found"):
		minter2.mint(2, {"from": accounts[2]})

	assert minter2.ownerOf(1) == accounts[1]

	chain.sleep(120)
	chain.mine()

	with reverts("Valid ticket not found"):
		minter2.mint(2, {"from": accounts[1]})

	balance_agent = agent.balance()
	balance_acc4 = accounts[4].balance()
	with reverts("Ownable: caller is not the owner"):
		agent.withdrawEther(accounts[4], {"from": accounts[1]})
	agent.withdrawEther(accounts[4])
	assert agent.balance() == 0
	assert accounts[4].balance() == balance_agent + balance_acc4
