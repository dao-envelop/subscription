import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket and call serviceProvider method
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1):

	#try to mint - serviceProvider is not registered
	with reverts("Valid ticket not found"):
		minter1.mint(1, {"from": accounts[1]})
	payOptions = [(dai, PRICE, 0), (weth, PRICE/5, 0)] #without Agent fee
	subscriptionType = (0,100,0,True, accounts[3])
	tariff1 = (subscriptionType, payOptions)
	#payOptions = [(dai, PRICE/4, 0), (weth, PRICE/10, 0)] #without Agent fee
	#subscriptionType = (0,100,0,True, accounts[3])

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	#register tariffs for service
	with reverts("Ownable: caller is not the owner"):
		minter1.registerServiceTariff(tariff1,{'from':accounts[1]})
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	#try to mint - serviceProvider is registered. But agent is not added
	with reverts("Valid ticket not found"):
		minter1.mint(1, {"from": accounts[1]})

	#register agent and tariffs for him
	with reverts("Ownable: caller is not the owner"):
		minter1.authorizeAgentForService(minter1.address, [0,1],{"from": accounts[1]})
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	#try to mint - serviceProvider is registered. Agent is added - self ServiceProvider. Ticket is not buyed
	with reverts("Valid ticket not found"):
		minter1.mint(1, {"from": accounts[1]})

	##buy subscription for time
	#non registered service
	with reverts(""):
		minter1.buySubscription(accounts[2], 1, 1, accounts[1], accounts[1], {"from": accounts[1]})

	#non exists tariff
	with reverts("Index out of range"):
		minter1.buySubscription(minter1.address, 1, 2, accounts[1], accounts[1], {"from": accounts[1]})

	#payer is not equal to msg.sender
	with reverts("ERC20: insufficient allowance"):
		minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[2], {"from": accounts[1]})

	pay_amount = payOptions[1][1]*(sub_reg.PERCENT_DENOMINATOR()+sub_reg.platformFeePercent())/sub_reg.PERCENT_DENOMINATOR()
	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	'''logging.info(
		'\nCalculated pay_amount:{}, '
		'\n  agent fee = {}'
		'\n  platform fee = {}'
		'\n-------------------'
		'\npay Amount from contract: {}'.format(
			pay_amount,
			payOptions[1][1]* payOptions[1][2]/sub_reg.PERCENT_DENOMINATOR(),
			payOptions[1][1]*sub_reg.platformFeePercent()/sub_reg.PERCENT_DENOMINATOR(),
			Wei(sub_reg.getTicketPrice(minter1.address, 0, 1)[1]).to('ether')
	))
	logging.info(sub_reg.getTariffsForService(minter1))'''

	minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})
	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	minter1.mint(1, {"from": accounts[1]})
        
	'''function buySubscription(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _buyFor,
        address _payer


        struct SubscriptionType {
        uint256 timelockPeriod;    // in seconds e.g. 3600*24*30*12 = 31104000 = 1 year
        uint256 ticketValidPeriod; // in seconds e.g. 3600*24*30    =  2592000 = 1 month
        uint256 counter;
        bool isAvailable;
        address beneficiary;
    }
    struct PayOption {
        address paymentToken;
        uint256 paymentAmount;
        uint16 agentFeePercent; // 100%-10000, 20%-2000, 3%-300 
    }'''









