# `SimpleAlgo`: An algo-trading environment for implementing Python-built strategies on MetaTrader5

## **SimpleAlgo is currently under active development**


The ultimate goal of `SimpleAlgo` is to create a one stop solution for deploying Machine Learning and Deep Learning strategies built in python. 

Currently, `SimpleAlgo` is fully functional in executing interval-based trading algorithms. 

### Deploying Strategies
A strategy compatible with `SimpleAlgo` inherits from the `Base` class, while main algo logic may be held in a separate file. The `Base` class handles data requests from MT5, and interval calculation. 

Orders are sent by packaging trade information using the `Trade_Package` class, and sent to the `Trade_Handler`, and places the order on the MT5 Terminal. 

Strategy files are to be placed in the `strategies` folder, which are automatically added to the strategy pool. 


### Limitations
Slower execution compared to MQL4, and therefore not ideal for high frequency trading. 

### Additional Features
A provision is created for storing executed trades in an SQL database using the `sqlalchemy` python package. 

## Disclaimer: Scripts used in this repository do not guarantee any profits and thus, should not be treated as financial advice. 