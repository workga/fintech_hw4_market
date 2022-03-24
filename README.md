# ...
This is a ...

### Features
- ...
- ...

### Endpoints

```
    /market/users
    /market/crypto
    /market/users/<string:login>/balance
    /market/users/<string:login>/portfolio
    /market/users/<string:login>/operations
```

### Usage

Create venv:
```bash
    make venv
```

Init and clear database:
```bash
    make init
```

Run application:
```bash
    make up
```

Remove temporary files:
```bash
    make clean
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
