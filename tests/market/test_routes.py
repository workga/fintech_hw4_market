import pytest

from app.market import market
from tests.market.conftest import formatted_now


def test_users_get(client):
    market.add_user('Annet')
    market.add_user('Bella')
    response = client.get('/market/users')

    data = response.get_json()
    assert len(data) == 2
    assert response.status_code == 200


def test_users_post(client):
    response = client.post('/market/users', json={'login': 'Annet'})

    assert len(market.get_users()) == 1
    assert response.status_code == 201


@pytest.mark.parametrize(
    'json',
    [
        None,
        {},
    ],
)
def test_users_post_invalid(client, json):
    response = client.post('/market/users', json=json)

    assert response.status_code == 422


def test_users_operaions_get(client):
    market.add_user('Annet')
    market.add_crypto('Favicoin', 200, 100)
    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Favicoin', 'sale', 10, formatted_now())

    response = client.get('/market/users/Annet/operations')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2


def test_users_operations_post(client):
    market.add_user('Annet')
    market.add_crypto('Favicoin', 200, 100)

    response = client.post(
        '/market/users/Annet/operations',
        json={
            'crypto_name': 'Favicoin',
            'operation_type': 'purchase',
            'amount': 10,
            'time_str': formatted_now(),
        },
    )

    assert response.status_code == 201


@pytest.mark.parametrize(
    'json',
    [
        None,
        {},
        {
            # 'crypto_name': 'Favicoin',
            'operation_type': 'purchase',
            'amount': 10,
            'time_str': formatted_now(),
        },
        {
            'crypto_name': 'Favicoin',
            # 'operation_type': 'purchase',
            'amount': 10,
            'time_str': formatted_now(),
        },
        {
            'crypto_name': 'Favicoin',
            'operation_type': 'purchase',
            # 'amount': 10,
            'time_str': formatted_now(),
        },
        {
            'crypto_name': 'Favicoin',
            'operation_type': 'purchase',
            'amount': 10,
            # 'time_str': formatted_now(),
        },
    ],
)
def test_users_operations_post_invalid(client, json):
    market.add_user('Annet')
    market.add_crypto('Favicoin', 200, 100)

    response = client.post('/market/users/Annet/operations', json=json)

    assert response.status_code == 422


def test_users_balance_get(client):
    market.add_user('Annet')
    market.add_crypto('Favicoin', 200, 100)
    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())

    response = client.get('/market/users/Annet/balance')
    data = response.get_json()

    assert response.status_code == 200
    assert data['balance'] == 1000 * 100 - 200 * 10


def test_users_portfolio_get(client):
    market.add_user('Annet')
    market.add_crypto('Favicoin', 200, 100)
    market.add_crypto('Geckcoin', 400, 200)

    market.add_operation('Annet', 'Favicoin', 'purchase', 10, formatted_now())
    market.add_operation('Annet', 'Geckcoin', 'purchase', 10, formatted_now())

    response = client.get('/market/users/Annet/portfolio')
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2


def test_crypto_get(client):
    market.add_crypto('Favicoin', 200, 100)
    market.add_crypto('Geckcoin', 400, 200)
    response = client.get('/market/crypto')

    data = response.get_json()
    assert len(data) == 2
    assert response.status_code == 200


def test_crypto_post(client):
    response = client.post(
        '/market/crypto',
        json={'crypto_name': 'Favicoin', 'purchase_cost': 200, 'sale_cost': 100},
    )

    assert len(market.get_crypto()) == 1
    assert response.status_code == 201


@pytest.mark.parametrize(
    'json',
    [
        None,
        {},
        {
            # 'crypto_name': 'Favicoin',
            'purchase_cost': 200,
            'sale_cost': 100,
        },
        {
            'crypto_name': 'Favicoin',
            # 'purchase_cost': 200,
            'sale_cost': 100,
        },
        {
            'crypto_name': 'Favicoin',
            'purchase_cost': 200,
            # 'sale_cost': 100
        },
    ],
)
def test_crypto_post_invalid(client, json):
    response = client.post(
        '/market/crypto',
        json=json,
    )

    assert response.status_code == 422
