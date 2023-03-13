import pytest
#from brownie import chain

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
    s = accounts[0].deploy(ServiceProvider,sub_reg, dai)
    yield s

@pytest.fixture(scope="module")
def singleAgent(accounts, Agent):
    a = accounts[0].deploy(Agent)
    yield a

@pytest.fixture(scope="module")
def serviceAndAgent(accounts, ServicAndAgent, dai, sub_reg):
    s = accounts[0].deploy(ServicAndAgent,sub_reg, dai)
    yield s

@pytest.fixture(scope="module")
def minter1(accounts, MinterServiceNoAgent, sub_reg):
    s = accounts[0].deploy(MinterServiceNoAgent,sub_reg, "Minter without Agent", 'MWA')
    yield s

