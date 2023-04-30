import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#zero price to buy subscription
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, EnvelopAgentWithRegistry, TokenMock, wrapper, wnft721):

	agent = accounts[0].deploy(EnvelopAgentWithRegistry)
	niftsy = accounts[0].deploy(TokenMock,"NIFTSY MOCK Token", "NIFTSY")

	payOptions = [(niftsy.address, 0,0 )] #without Agent fee
	subscriptionType = (0,0,1,True,'0xDDA2F2E159d2Ce413Bd0e1dF5988Ee7A803432E3')
	tariff1 = (subscriptionType, payOptions)

	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(niftsy, True, {'from':accounts[0]})
	
	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})

	minter1.authorizeAgentForService(agent.address, [0],{"from": accounts[0]})

	agent.buySubscription(minter1.address, 0, 0, accounts[2], accounts[1], {"from": accounts[1]})

	assert minter1.checkUserSubscription(accounts[2])[0] == True
	assert sub_reg.getUserTicketForService(minter1.address, accounts[2])[1] == 1
	assert sub_reg.getUserTicketForService(minter1.address, accounts[2])[0] > 0
	