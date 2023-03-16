import pytest
import logging
from brownie import chain, Wei, reverts
LOGGER = logging.getLogger(__name__)
from web3 import Web3




def test_add_payments(accounts, dai, weth, sub_reg):
    sub_reg.setAssetForPaymentState(dai, True, {'from':accounts[0]})
    sub_reg.setAssetForPaymentState(weth, True, {'from':accounts[0]})
    assert sub_reg.whiteListedForPayments(dai) == True
    assert sub_reg.whiteListedForPayments(weth) == True
    
def test_register_agent(accounts, dai, weth, sub_reg, serviceAndAgent): 
    serviceAndAgent.setAgent({'from':accounts[0]})
    actual_tarifs = sub_reg.getAvailableAgentsTariffForService(serviceAndAgent, serviceAndAgent)
    logging.info(
        'Service:({}, agent {}),'
        '\ntarifs = {}'.format(
            serviceAndAgent,
            serviceAndAgent,
            actual_tarifs
    ))
    assert len(actual_tarifs) == 1    

def test_buy_ticket(accounts, dai, weth, sub_reg, serviceAndAgent):
    actual_tarifs = sub_reg.getAvailableAgentsTariffForService(serviceAndAgent, serviceAndAgent)
    dai.transfer(accounts[1], actual_tarifs[0][1][0][1]*20, {'from':accounts[0]})
    dai.approve(sub_reg, actual_tarifs[0][1][0][1]*20, {'from':accounts[1]})
    logging.info('Ticket price:{}'.format(sub_reg.getTicketPrice(serviceAndAgent,0,0)))
    ticket = serviceAndAgent.buyTicket({'from':accounts[1]})
    user_tickets = sub_reg.getUserTicketForService(serviceAndAgent, accounts[1])
    logging.info(
        '\nService:({}, agent {}),'
        '\njust purchaced ticket = {}'
        '\n agetUserTicketForService: {}'.format(
            serviceAndAgent,
            serviceAndAgent,
            ticket.return_value,
            user_tickets
    ))         

def test_get_service(accounts, dai, weth, sub_reg, serviceAndAgent):
    tx = serviceAndAgent.getService(99,{'from':accounts[1]})
    logging.info('Events: {}'.format(tx.events['ServiceOK']))
    assert tx.events['ServiceOK']['param'] == 99

def test_buy_ticket_ether(accounts, dai, weth, sub_reg, serviceAndAgent):
    actual_tarifs = sub_reg.getAvailableAgentsTariffForService(serviceAndAgent, serviceAndAgent)
    logging.info('Ticket price:{}'.format(sub_reg.getTicketPrice(serviceAndAgent,0,1)))
    ticket = serviceAndAgent.buyTicketWithEther({'value': 1e18, 'from':accounts[1]})
    user_tickets = sub_reg.getUserTicketForService(serviceAndAgent, serviceAndAgent)
    logging.info(
        'Service:({}, agent {}),'
        '\nticket = {}'.format(
            serviceAndAgent,
            serviceAndAgent,
            ticket.return_value
    ))             