from typing import Optional, Tuple

from flask import Blueprint, Response, jsonify, request

from app.market import exceptions, market

bp = Blueprint('market', __name__)


@bp.errorhandler(exceptions.MarketError)
def handle_market_error(error: exceptions.MarketError) -> Tuple[Response, int]:
    return jsonify(error.as_dict()), error.status_code


@bp.route('/users', methods=['GET', 'POST'])
def users() -> Optional[Response]:
    '''
    GET - Get list of users
    POST - Register new user
    '''
    if request.method == 'GET':

        users_list = market.get_users()

        return jsonify(users_list)

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return Response(status=422)
        try:
            login = data['login']
        except KeyError:
            return Response(status=422)

        market.add_user(login)

        return Response(status=201)

    return None


@bp.route('/users/<string:login>/operations', methods=['GET', 'POST'])
def users_operations(login: str) -> Optional[Response]:
    '''
    GET - Get history of user's operations
    POST - Sale or purchase crypto
    '''
    if request.method == 'GET':

        operations_list = market.get_operations(login)

        return jsonify(operations_list)

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return Response(status=422)
        try:
            crypto_name = data['crypto_name']
            operation_type = data['operation_type']
            amount = data['amount']
            time_str = data['time_str']
        except KeyError:
            return Response(status=422)

        market.add_operation(login, crypto_name, operation_type, amount, time_str)

        return Response(status=201)

    return None


@bp.route('/users/<string:login>/balance', methods=['GET'])
def users_balance(login: str) -> Optional[Response]:
    '''
    GET - Get users's balance
    '''
    if request.method == 'GET':

        balance = market.get_balance(login)

        return jsonify(balance)

    return None


@bp.route('/users/<string:login>/portfolio', methods=['GET'])
def users_portfolio(login: str) -> Optional[Response]:
    '''
    GET - Get user's portfolio of crypto
    '''
    if request.method == 'GET':

        portfolio_list = market.get_portfolio(login)

        return jsonify(portfolio_list)

    return None


@bp.route('/crypto', methods=['GET', 'POST'])
def crypto() -> Optional[Response]:
    '''
    GET - Get list of crypto
    POST - Add new crypto
    '''
    if request.method == 'GET':

        crypto_list = market.get_crypto()

        return jsonify(crypto_list)

    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return Response(status=422)
        try:
            crypto_name = data['crypto_name']
            purchase_cost = data['purchase_cost']
            sale_cost = data['sale_cost']
        except KeyError:
            return Response(status=422)

        market.add_crypto(crypto_name, purchase_cost, sale_cost)

        return Response(status=201)

    return None
