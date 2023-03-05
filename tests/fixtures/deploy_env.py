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
def usdt(accounts, TokenMock):
    w = accounts[0].deploy(TokenMock,"USDT MOCK Token", "USDT")
    yield w

@pytest.fixture(scope="module")
def erc721mock(accounts, Token721Mock):
    """
    NFT 721 with URI
    """
    t = accounts[0].deploy(Token721Mock, "Simple NFT with URI", "XXX")
    t.setURI(0, 'https://maxsiz.github.io/')
    yield t  

@pytest.fixture(scope="module")
def erc1155mock(accounts, Token1155Mock):
    """
    NFT 1155 with URI
    """
    t = accounts[0].deploy(Token1155Mock, "https://maxsiz.github.io/")
    yield t  

#######################light version of protocol########################3
@pytest.fixture(scope="module")
def wrapper(accounts, pm):
    wa = pm('envelopv1').WrapperLightV1
    w = accounts[0].deploy(wa)
    yield w

@pytest.fixture(scope="module")
def wnft721(accounts, pm, wrapper):
    wa = pm('envelopv1').EnvelopwNFT721Trustless
    wnft = accounts[0].deploy(wa,"Envelop wNFT", "eNFT", "https://api.envelop.is/metadata/", wrapper )
    yield wnft

@pytest.fixture(scope="module")
def wnft1155(accounts, pm, wrapper):
    wa = pm('envelopv1').EnvelopwNFT1155Trustless
    wnft = accounts[0].deploy(EnvelopwNFT1155Trustless,"Envelop wNFT", "eNFT", "https://api.envelop.is/metadata/", wrapper)
    yield wnft

##################### Main contracts##################
@pytest.fixture(scope="module")
def kiosk(accounts, EnvelopNFTKiosk):
    k = accounts[0].deploy(EnvelopNFTKiosk, accounts[0])
    yield k

@pytest.fixture(scope="module")
def DefPrModal(accounts, DefaultPriceModel, kiosk):
    d = accounts[0].deploy(DefaultPriceModel, kiosk)
    yield d


@pytest.fixture(scope="module")
def erc721Hack(accounts, ERC721Hack, kiosk):
    t = accounts[0].deploy(ERC721Hack, "Simple NFT with URI", "XXX", kiosk.address)
    yield t  
