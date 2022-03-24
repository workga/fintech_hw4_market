from flask import Blueprint, Response, jsonify, request

from app.market import exceptions, market

bp = Blueprint('market', __name__)


@bp.errorhandler(exceptions.MarketError)
def handle_market_error(error):
    return jsonify(error.as_dict()), error.status_code


@bp.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        '''
        Get list of users
        '''

        users = market.get_users()

        return jsonify(users)

    if request.method == 'POST':
        '''
        Register new user
        '''
        login = request.args.get('login', type=str)
        market.add_user(login)

        return Response(status=200)

    return None


@bp.route('/users/<string:login>/operations', methods=['GET', 'POST'])
def users_operations(login):
    if request.method == 'GET':
        '''
        Get history of user's operations
        '''
        operations = market.get_operations(login)

        return jsonify(operations)

    if request.method == 'POST':
        '''
        Sale or purchase crypto
        '''
        crypto_name = request.args.get('crypto_name', type=str)
        operation_type = request.args.get('operation_type', type=str)
        amount = request.args.get('amount', type=int)
        time = request.args.get('time', type=str)

        market.add_operation(login, crypto_name, operation_type, amount, time)

        return Response(status=200)

    return None


@bp.route('/users/<string:login>/balance', methods=['GET'])
def users_balance(login):
    if request.method == 'GET':
        '''
        Get users's balance
        '''

        balance = market.get_balance(login)

        return jsonify(balance)

    return None


@bp.route('/users/<string:login>/portfolio', methods=['GET'])
def users_portfolio(login):
    if request.method == 'GET':
        '''
        Get user's portfolio of crypto
        '''

        portfolio = market.get_portfolio(login)

        return jsonify(portfolio)

    return None


@bp.route('/crypto', methods=['GET', 'POST'])
def crypto():
    if request.method == 'GET':
        '''
        Get list of crypto
        '''

        crypto = market.get_crypto()

        return jsonify(crypto)

    if request.method == 'POST':
        '''
        Add new crypto
        '''

        crypto_name = request.args.get('crypto_name', type=str)
        purchase_cost = request.args.get('purchase_cost', type=int)
        sale_cost = request.args.get('sale_cost', type=int)
        market.add_crypto(crypto_name, purchase_cost, sale_cost)

        return Response(status=200)

    return None
