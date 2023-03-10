// SPDX-License-Identifier: MIT
// ENVELOP(NIFTSY) protocol V1 for NFT. Subscription Manager Contract V2
pragma solidity 0.8.16;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@envelopv1/interfaces/ITrustedWrapper.sol";
import "@envelopv1/interfaces/ISubscriptionManager.sol";
import "@envelopv1/contracts/LibEnvelopTypes.sol";
//import "./LibEnvelopTypes.sol";

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
    }

    struct Tariff {
        SubscriptionType subscription;
        PayOption[] payWith;
    }

    // native subscribtionManager tickets format
    struct Ticket {
        uint256 validUntil; // Unixdate, tickets not valid after
        uint256 countsLeft; // for tarif with fixed use counter
    }

contract SubscriptionRegistry is Ownable {
    using SafeERC20 for IERC20;

    uint256 constant public PERCENT_DENOMINATOR = 10000;

    address public platformOwner; // Envelop Multisig
    uint16 public platformFeePercent = 50; // 100%-10000, 20%-2000, 3%-300



    address  public mainWrapper;
    address  public previousRegistry;

    mapping(address => bool) public whiteListedForPayments;
    
    // from service(=smart contract address) to tarifs
    mapping(address => Tariff[]) public availableTariffs;

    // from service to agent to available tarifs(tarif index);
    mapping(address => mapping(address => uint256[])) public agentServiceRegistry;
     
    
    // mapping from user addres to service contract address  to ticket
    mapping(address => mapping(address => Ticket)) public userTickets;

    // TODO Events

    constructor(address _platformOwner) {
        require(_platformOwner != address(0),'Zero platform fee receiver');
        platformOwner = _platformOwner;
    } 
   
    function registerServiceTarif(Tariff calldata _newTarif) 
        external 
        returns(uint256)
    {
        // TODO
        // Tarif structure check
        // PayWith array whiteList check
        return _addTarif(msg.sender, _newTarif);
    }

    function editServiceTarif(
        uint256 _tarifIndex, 
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod,
        uint256 _counter,
        bool _isAvailable,
        address _beneficiary
    ) 
        external
    {
        // TODO
        // Tarif structure check
        // PayWith array whiteList check
        _editTarif(
            msg.sender,
            _tarifIndex, 
            _timelockPeriod,
            _ticketValidPeriod,
            _counter,
            _isAvailable,
            _beneficiary
        );

    }

    function addTarifPayOption(
        uint256 _tarifIndex,
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external returns(uint256)
    {
        return _addTarifPayOption(
            msg.sender,
            _tarifIndex,
            _paymentToken,
            _paymentAmount,
            _agentFeePercent
        );
    }

    function editTarifPayOption(
        uint256 _tarifIndex,
        uint256 _payWithIndex, 
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) external 
    {
        _editTarifPayOption(
            msg.sender,
            _tarifIndex,
            _payWithIndex, 
            _paymentToken,
            _paymentAmount,
            _agentFeePercent
        );
    }

    // Only service contract must call this function
    function authorizeAgentForService(
        address _agent,
        // uint256 _platformTarifIndex,
        // uint256 _payWithIndex,
        // address _payer,
        uint256[] calldata _serviceTarifIndexes
    ) external virtual returns (uint256[] memory) 
    {
        // remove previouse tarifs
        delete agentServiceRegistry[msg.sender][_agent];
        uint256[] storage currentServiceTarifsOfAgent = agentServiceRegistry[msg.sender][_agent];
        // check that adding tarifs still available
        for(uint256 i; i < _serviceTarifIndexes.length; ++ i) {
            if (availableTariffs[msg.sender][_serviceTarifIndexes[i]].subscription.isAvailable){
                currentServiceTarifsOfAgent.push(_serviceTarifIndexes[i]);
            }
        }
        return currentServiceTarifsOfAgent;
    }
    
    // Available only for agents
    function buySubscription(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _buyFor,
        address _payer
    ) external 
      returns(Ticket memory ticket) {
        // Cant buy ticket for nobody
        require(_buyFor != address(0),'Cant buy ticket for nobody');

        require(
            availableTariffs[_service][_tarifIndex].subscription.isAvailable,
            'This subscription not available'
        );

        require(
            availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount > 0,
            'This Payment option not available'
        );

        // Check that agent is authorized for purchace of this service
        require(
            _isAgentAuthorized(msg.sender, _service, _tarifIndex), 
            'Agent not authorized for this service tarif' 
        );
        
        (bool isValid, bool needFix) = _isTicketValid(_buyFor, _service);
        require(!isValid, 'Only one valid ticket at time');

        //lets safe user ticket (only one ticket available in this version)
        userTickets[_buyFor][_service] = Ticket(
            availableTariffs[_service][_tarifIndex].subscription.ticketValidPeriod + block.timestamp,
            availableTariffs[_service][_tarifIndex].subscription.counter
        );

        // Lets receive payment tokens FROM sender
        _processPayment(_service, _tarifIndex, _payWithIndex, _payer);
        

    }

    function checkAndFixUserSubscription(
        address _user
    ) external returns (bool ok){
        
        //address _service = msg.sender;
        // Check user ticket
        (bool isValid, bool needFix) = _isTicketValid(_user, msg.sender);
        
        // Proxy to previos
        // if (!isValid && previousRegistry != address(0)) {
        //     isValid = ISubscriptionManager(previousManager).checkUserSubscription(
        //         _user, 
        //         _service
        //     );
        //     // Case when valid ticket stored in previousManager
        //     if (isValid) {
        //         ISubscriptionManager(previousManager).fixUserSubscription(
        //             _user, 
        //             _service
        //         );
        //         ok = true;
        //         return ok;
        //     }
        // }
        require(isValid,'Valid ticket not found');
        
        // Fix action (for subscription with counter)
        if (needFix){
            fixUserSubscription(_user);    
        }
                
        ok = true;
    }

    function fixUserSubscription(
        address _user
    ) public {
        // Fix action (for subscription with counter)
        if (userTickets[_user][msg.sender].countsLeft > 0) {
            -- userTickets[_user][msg.sender].countsLeft; 
        }
    }

    ////////////////////////////////////////////////////////////////
    
    function checkUserSubscription(
        address _user, 
        address _service
    ) external view returns (bool ok) {
        (ok,)  = _isTicketValid(_user, _service);
        // if (!ok && previousManager != address(0)) {
        //     ok = ISubscriptionManager(previousManager).checkUserSubscription(
        //         _user, 
        //         _serviceCode
        //     );
        // }
    }

    function getUserTicketForService(
        address _service,
        address _user
    ) public view returns(Ticket memory) 
    {
        return userTickets[_user][_service];
    }

    function getTariffsForService(address _service) external view returns (Tariff[] memory) {
        return availableTariffs[_service];
    }

    function getTicketPrice(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex
    ) public view virtual returns (address, uint256) 
    {
        if (availableTariffs[_service][_tarifIndex].subscription.timelockPeriod != 0)
        {
            return(
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken,
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
            );
        } else {
            return(
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken,
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                + availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                    *availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].agentFeePercent
                    /PERCENT_DENOMINATOR
                + availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                        *_platformFeePercent(_service, _tarifIndex, _payWithIndex) 
                        /PERCENT_DENOMINATOR
            );
        }
    }

    function getAvailableAgentsTarifForService(
        address _agent, 
        address _service
    ) external view virtual returns(Tariff[] memory) 
    {
        //First need get count of tarifs that still available
        uint256 availableCount;
        for (uint256 i; i < agentServiceRegistry[_service][_agent].length; ++i){
            if (availableTariffs[_service][
                  agentServiceRegistry[_service][_agent][i]
                ].subscription.isAvailable
            ) {++availableCount;}
        }
        
        Tariff[] memory result = new Tariff[](availableCount);
        for (uint256 i; i < agentServiceRegistry[_service][_agent].length; ++i){
            if (availableTariffs[_service][
                  agentServiceRegistry[_service][_agent][i]
                ].subscription.isAvailable
            ) 
            {
                result[availableCount - 1] = availableTariffs[_service][
                  agentServiceRegistry[_service][_agent][i]
                ];
                --availableCount;
            }
        }
        return result;

    }    
    ////////////////////////////////////////////////////////////////
    //////////     Admins                                     //////
    ////////////////////////////////////////////////////////////////

    function setAssetForPaymentState(address _asset, bool _isEnable)
        external onlyOwner 
    {
        whiteListedForPayments[_asset] = _isEnable;
    }

    function setMainWrapper(address _wrapper) external onlyOwner {
        mainWrapper = _wrapper;
    }

    function setPlatformOwner(address _newOwner) external {
        require(msg.sender == platformOwner, 'Only platform owner');
        require(_newOwner != address(0),'Zero platform fee receiver');
        platformOwner = _newOwner;
    }

    // function registerPlatformTarif(Tariff calldata _newTarif) 
    //     external onlyOwner
    //     returns(uint256)
    // {
    //     // TODO
    //     // Tarif structure check
    //     // PayWith array whiteList check
    //     _addTarif(address(this), _newTarif);
    // }

    // function editPlatformTarif(
    //     uint256 _tarifIndex, 
    //     uint256 _timelockPeriod,
    //     uint256 _ticketValidPeriod,
    //     uint256 _counter,
    //     bool _isAvailable,
    //     address _beneficiary
    // ) 
    //     external onlyOwner
    // {
    //     // TODO
    //     // Tarif structure check
    //     // PayWith array whiteList check
    //     _editTarif(
    //         address(this),
    //         _tarifIndex, 
    //         _timelockPeriod,
    //         _ticketValidPeriod,
    //         _counter,
    //         _isAvailable,
    //         _beneficiary
    //     );

    // }

    // function addPlatformTarifPayOption(
    //     uint256 _tarifIndex,
    //     address _paymentToken,
    //     uint256 _paymentAmount,
    //     uint16 _agentFeePercent
    // ) external onlyOwner returns(uint256)
    // {
    //     return _addTarifPayOption(
    //         address(this),
    //         _tarifIndex,
    //         _paymentToken,
    //         _paymentAmount,
    //         _agentFeePercent
    //     );
    // }

    // function editPlatformTarifPayOption(
    //     uint256 _tarifIndex,
    //     uint256 _payWithIndex, 
    //     address _paymentToken,
    //     uint256 _paymentAmount,
    //     uint16 _agentFeePercent
    // ) external onlyOwner
    // {
    //     _editTarifPayOption(
    //         address(this),
    //         _tarifIndex,
    //         _payWithIndex, 
    //         _paymentToken,
    //         _paymentAmount,
    //         _agentFeePercent
    //     );
    // }

    function setPreviousRegistry(address _registry) external onlyOwner {
        previousRegistry = _registry;
    }
    /////////////////////////////////////////////////////////////////////
    
    function _processPayment(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex,
        address _payer
    ) 
        internal 
        virtual 
        returns(bool)
    {
        // there are two payment method for this implementation.
        // 1. with wrap and lock in asset (no fees)
        // 2. simple payment (agent & platform fee enabled)
        if (availableTariffs[_service][_tarifIndex].subscription.timelockPeriod != 0){
            require(msg.value == 0, 'Ether Not accepted in this method');
            // 1. with wrap and lock in asset
            IERC20(
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
            ).safeTransferFrom(
                _payer, 
                address(this),
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
            );

            // Lets approve received for wrap 
            IERC20(
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
            ).safeApprove(
                mainWrapper,
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
            );

            // Lets wrap with timelock and appropriate params
            ETypes.INData memory _inData;
            ETypes.AssetItem[] memory _collateralERC20 = new ETypes.AssetItem[](1);
            ETypes.Lock[] memory timeLock =  new ETypes.Lock[](1);
            // Only need set timelock for this wNFT
            timeLock[0] = ETypes.Lock(
                0x00, // timelock
                availableTariffs[_service][_tarifIndex].subscription.timelockPeriod + block.timestamp
            ); 
            _inData = ETypes.INData(
                ETypes.AssetItem(
                    ETypes.Asset(ETypes.AssetType.EMPTY, address(0)),
                    0,0
                ),          // INAsset
                address(0), // Unwrap destinition    
                new ETypes.Fee[](0), // Fees
                //new ETypes.Lock[](0), // Locks
                timeLock,
                new ETypes.Royalty[](0), // Royalties
                ETypes.AssetType.ERC721, // Out type
                0, // Out Balance
                0x0000 // Rules
            );

            _collateralERC20[0] = ETypes.AssetItem(
                ETypes.Asset(
                    ETypes.AssetType.ERC20,
                    availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
                ),
                0,
                availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
            );
            
            ITrustedWrapper(mainWrapper).wrap(
                _inData,
                _collateralERC20,
                _payer
            );

        } else {
            // 2. simple payment
            if (availableTariffs[_service][_tarifIndex]
                .payWith[_payWithIndex]
                .paymentToken != address(0)
            ) 
            {
                // pay with erc20 
                require(msg.value == 0, 'Ether Not accepted in this method');
                // 2.1. Body payment  
                IERC20(
                    availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
                ).safeTransferFrom(
                    _payer, 
                    availableTariffs[_service][_tarifIndex].subscription.beneficiary,
                    availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                );

                // 2.2. Agent fee payment
                IERC20(
                    availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
                ).safeTransferFrom(
                    _payer, 
                    msg.sender,
                    availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                    *100/availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].agentFeePercent
                );

                // 2.3. Platform fee 
                uint256 _pFee = _platformFeePercent(_service, _tarifIndex, _payWithIndex); 
                if (_pFee > 0) {
                    IERC20(
                        availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentToken
                    ).safeTransferFrom(
                        _payer, 
                        platformOwner, //
                        availableTariffs[_service][_tarifIndex].payWith[_payWithIndex].paymentAmount
                        *100/_pFee
                    );
                }

            } else {
              // pay with native token(eth, bnb, etc)
            }
        }
    }

    // In this impementation params not used. 
    // Can be ovveriden in other cases
    function _platformFeePercent(
        address _service, 
        uint256 _tarifIndex, 
        uint256  _payWithIndex
    ) internal view virtual returns(uint256) 
    {
        return platformFeePercent;
    }

    function _addTarif(address _service, Tariff calldata _newTarif) 
        internal returns(uint256) 
    {
        require (_newTarif.payWith.length > 0, 'No payment method');
        availableTariffs[_service].push(_newTarif);
        return availableTariffs[_service].length - 1;
    }

    // function _removeTarif(address _service, uint256 _tarifIndex) 
    //     internal  
    // {
    //     //TODO
    //     //Check that there is no agents with active tickets
    //     delete availableTariffs[_service];
    // }

    function _editTarif(
        address _service,
        uint256 _tarifIndex, 
        uint256 _timelockPeriod,
        uint256 _ticketValidPeriod,
        uint256 _counter,
        bool _isAvailable,
        address _beneficiary
    ) internal  
    {
        availableTariffs[_service][_tarifIndex].subscription.timelockPeriod    = _timelockPeriod;
        availableTariffs[_service][_tarifIndex].subscription.ticketValidPeriod = _ticketValidPeriod;
        availableTariffs[_service][_tarifIndex].subscription.counter = _counter;
        availableTariffs[_service][_tarifIndex].subscription.isAvailable = _isAvailable;    
        availableTariffs[_service][_tarifIndex].subscription.beneficiary = _beneficiary;    
    }
   
    function _addTarifPayOption(
        address _service,
        uint256 _tarifIndex,
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) internal returns(uint256)
    {
        availableTariffs[_service][_tarifIndex].payWith.push(
            PayOption(_paymentToken, _paymentAmount, _agentFeePercent)
        ); 
        return availableTariffs[_service][_tarifIndex].payWith.length - 1;
    }

    function _editTarifPayOption(
        address _service,
        uint256 _tarifIndex,
        uint256 _payWithIndex, 
        address _paymentToken,
        uint256 _paymentAmount,
        uint16 _agentFeePercent
    ) internal  
    {
        availableTariffs[_service][_tarifIndex].payWith[_payWithIndex] 
        = PayOption(_paymentToken, _paymentAmount, _agentFeePercent);    
    }

        
   function _isTicketValid(address _user, address _service) 
        internal 
        view 
        returns (bool isValid, bool needFix ) 
    {
        isValid =  userTickets[_user][_service].validUntil > block.timestamp 
            || userTickets[_user][_service].countsLeft > 0;
        needFix =  userTickets[_user][_service].countsLeft > 0;   
    }

    function _isAgentAuthorized(
        address _agent, 
        address _service, 
        uint256 _tarifIndex
    ) 
        internal
        view
        returns(bool authorized)
    {
        for (uint256 i; i < agentServiceRegistry[_service][_agent].length; ++ i){
            if (agentServiceRegistry[_service][_agent][i] == _tarifIndex){
                authorized = true;
                return authorized;
            }
        }
    }
}