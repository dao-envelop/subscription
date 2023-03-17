import pytest
#from brownie import chain
zero_address = '0x0000000000000000000000000000000000000000'
############ Mocks ########################
@pytest.fixture(scope="module")
def dai(accounts, TokenMock):
    dai = accounts[0].deploy(TokenMock,"DAI MOCK Token", "DAI")
    yield dai

@pytest.fixture(scope="module")
def weth(accounts, TokenMock):
    w = accounts[0].deploy(TokenMock,"WETH MOCK Token", "WETH")
    yield w

@pytest.fixture(scope="module")
def sub_reg(accounts, SubscriptionRegistry):
    r = accounts[0].deploy(SubscriptionRegistry, accounts[0].address)
    yield r
#-------------------------------------------------------------------
@pytest.fixture(scope="module")
def singleServiceProvider(accounts, ServiceProvider, dai, sub_reg):
    sub_reg.setAssetForPaymentState(dai.address, True, {'from':accounts[0]})
    s = accounts[0].deploy(ServiceProvider,sub_reg, dai)
    yield s

@pytest.fixture(scope="module")
def singleAgent(accounts, Agent):
    a = accounts[0].deploy(Agent)
    yield a

@pytest.fixture(scope="module")
def serviceAndAgent(accounts, ServiceAndAgent, dai, weth, sub_reg):
    sub_reg.setAssetForPaymentState(dai.address, True, {'from':accounts[0]})
    sub_reg.setAssetForPaymentState(zero_address, True, {'from':accounts[0]})
    #sub_reg.setAssetForPaymentState(weth.address, True, {'from':accounts[0]})
    s = accounts[0].deploy(ServiceAndAgent,sub_reg, dai)
    yield s

@pytest.fixture(scope="module")
def minter1(accounts, MinterServiceNoAgent, sub_reg):
    s = accounts[0].deploy(MinterServiceNoAgent,sub_reg, "Minter without Agent", 'MWA1')
    yield s

@pytest.fixture(scope="module")
def minter2(accounts, MinterServiceWithAgent, sub_reg):
    s = accounts[0].deploy(MinterServiceWithAgent, sub_reg, "Minter with Agent", 'MWA2')
    yield s

@pytest.fixture(scope="module")
def agent(accounts, Agent):
    s = accounts[0].deploy(Agent)
    yield s

@pytest.fixture(scope="module")
def wrapper(accounts, pm):
    wa = pm('envelopv1').WrapperLightV1
    w = accounts[0].deploy(wa)
    yield w

@pytest.fixture(scope="module")
def wnft721(accounts, pm):
    wa = pm('envelopv1').EnvelopwNFT721
    wnft = accounts[0].deploy(wa,"Envelop wNFT", "eNFT", "https://api.envelop.is/metadata/" )
    yield wnft

