# Crypto Market
This is Crypto Market web application implemeted as json API.

### Features
- Autoupdate of exchange rate
- Timelimit for exchange rate: you can't use outdated rate

### Endpoints
```
    /market/users
    GET - Get list of users
    POST - Register new user

    /market/crypto
    GET - Get list of crypto
    POST - Add new crypto

    /market/users/<string:login>/balance
    GET - Get users's balance
    
    /market/users/<string:login>/operations
    GET - Get history of user's operations
    POST - Sale or purchase crypto
   
    /market/users/<string:login>/portfolio
    GET - Get user's portfolio of crypto 
```

### Usage

Create venv:
```bash
    make venv
```

Clear database:
```bash
    make clear-db
```

Run application:
```bash
    make up
```

### Development
Run tests:
```bash
    make test
```

Run linters:
```bash
    make lint
```

Run formatters:
```bash
    make format
```
