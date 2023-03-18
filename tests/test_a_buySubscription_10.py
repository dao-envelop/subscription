import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider has Agent. Buy ticket for erc20 and call agent buySubscription method. With Agent. Ticket is with expiring time
def test_buy_subscription(accounts, dai, weth, sub_reg, minter2, agent):

	payOptions = [(dai, PRICE, 100), (weth, PRICE/5, 100)] #with Agent fee
	subscriptionType = (0,100,0,True, accounts[3])
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	#register tariffs for service
	minter2.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter2.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})
	
	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent() + payOptions[1][2])/sub_reg.PERCENT_DENOMINATOR()

	#pay for erc20
	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})

	before_acc1 = weth.balanceOf(accounts[1])
	before_acc0 = weth.balanceOf(accounts[0])
	before_acc3 = weth.balanceOf(accounts[3])
	before_agent = weth.balanceOf(agent.address)
	agent.buySubscription(minter2.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})

	ticket = sub_reg.getUserTicketForService(minter2.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert weth.balanceOf(accounts[1]) == before_acc1 - pay_amount # payer balance
	assert weth.balanceOf(accounts[0]) == before_acc0 + payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR() # planform beneficiary balance
	assert weth.balanceOf(accounts[3]) == before_acc3 + payOptions[1][1] # serviceProvider beneficiary balance
	assert weth.balanceOf(agent) == before_agent + payOptions[1][1]*payOptions[1][2]/sub_reg.PERCENT_DENOMINATOR() #  agent balance

	minter2.mint(1, {"from": accounts[1]})

	assert minter2.ownerOf(1) == accounts[1]

	chain.sleep(120)
	chain.mine()

	with reverts("Valid ticket not found"):
		minter2.mint(2, {"from": accounts[1]})

	balance_agent = weth.balanceOf(agent)
	balance_acc4 = weth.balanceOf(accounts[4])
	with reverts("Ownable: caller is not the owner"):
		agent.withdrawERC20Tokens(weth.address, accounts[4], {"from": accounts[1]})
	agent.withdrawERC20Tokens(weth.address, accounts[4])
	assert weth.balanceOf(agent) == 0
	assert weth.balanceOf(accounts[4]) == balance_agent + balance_acc4