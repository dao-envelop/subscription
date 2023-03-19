import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3


PRICE = 1e18
zero_address = '0x0000000000000000000000000000000000000000'

#service provider is selfAgent. Buy ticket by wrapping erc20 tokens and call serviceProvider method. Without Agent. Ticket is with expiring time
def test_buy_subscription(accounts, dai, weth, sub_reg, minter1, wrapper, wnft721):

	#set wrapper
	with reverts("Ownable: caller is not the owner"):
		sub_reg.setMainWrapper(wrapper.address, {"from": accounts[1]})
	sub_reg.setMainWrapper(wrapper.address, {"from": accounts[0]})

	payOptions = [(dai, PRICE, 100), (weth, PRICE/5, 100)] #with Agent fee - agent does not have to get any erc20 tokens
	subscriptionType = (200,100,0,True, accounts[9]) #with service Provider beneficiary - special case 
	tariff1 = (subscriptionType, payOptions)
	
	#add tokens to whiteList
	sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
	sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})

	#register tariffs for service
	minter1.registerServiceTariff(tariff1,{'from':accounts[0]})
	#register agent - self service Provider
	minter1.authorizeAgentForService(minter1.address, [0],{"from": accounts[0]})

	if (wrapper.lastWNFTId(3)[1] == 0):
		wrapper.setWNFTId(3, wnft721.address, 0, {'from':accounts[0]})
	wnft721.setMinter(wrapper.address, {"from": accounts[0]})
	
	pay_amount = payOptions[1][1]

	#pay for ether  - #more than necessary
	with reverts("Ether Not accepted in this method"):
		minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1], "value": pay_amount})

	with reverts("ERC20: insufficient allowance"):
		minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})
	pay_amount = payOptions[1][1]
	weth.approve(sub_reg.address, pay_amount, {"from": accounts[1]})
	with reverts("ERC20: transfer amount exceeds balance"):
		minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})

	weth.transfer(accounts[1], pay_amount, {"from": accounts[0]})

	before_acc1 = weth.balanceOf(accounts[1])
	before_w = weth.balanceOf(wrapper.address)

	tx = minter1.buySubscription(minter1.address, 0, 1, accounts[1], accounts[1], {"from": accounts[1]})
	wTokenId = tx.events['WrappedV1']['outTokenId']


	ticket = sub_reg.getUserTicketForService(minter1.address, accounts[1])
	assert ticket[0] > 0
	assert ticket[1] == subscriptionType[2]

	#check balance
	assert weth.balanceOf(accounts[1]) == before_acc1 - pay_amount # payer balance
	assert weth.balanceOf(wrapper.address) == before_w + pay_amount # wrapper balance
	assert weth.balanceOf(accounts[9]) == 0
	assert weth.balanceOf(minter1) == 0


	minter1.mint(1, {"from": accounts[1]})

	assert minter1.ownerOf(1) == accounts[1]
	assert wnft721.balanceOf(accounts[1]) == 1 #check wnft
	assert wnft721.balanceOf(accounts[9]) == 0

	#check wnft
	assert wnft721.wnftInfo(wTokenId)[0] == ((0, zero_address), 0, 0) 
	assert wnft721.wnftInfo(wTokenId)[1][0] == ((2, weth.address), 0, int(pay_amount))
	assert wnft721.wnftInfo(wTokenId)[2] == zero_address
	assert wnft721.wnftInfo(wTokenId)[3] == []
	assert wnft721.wnftInfo(wTokenId)[4][0][1] > chain.time() 
	assert wnft721.wnftInfo(wTokenId)[5] == []
	assert wnft721.wnftInfo(wTokenId)[6] == '0x0000'

	#check event
	assert tx.events['TicketIssued']['service'] == minter1.address
	assert tx.events['TicketIssued']['agent'] == minter1.address
	assert tx.events['TicketIssued']['forUser'] == accounts[1]
	assert tx.events['TicketIssued']['tariffIndex'] == 0

	chain.sleep(120)
	chain.mine()

	#ticket expired
	with reverts("Valid ticket not found"):
		minter1.mint(1, {"from": accounts[1]})
  




