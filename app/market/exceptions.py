from sqlalchemy.exc import SQLAlchemyError


class MarketError(Exception):
    def __init__(self, message='Market Error', status_code=400, payload=None):
        self.message = message
        self.payload = payload
        self.status_code = status_code

        super().__init__(self.message)

    def as_dict(self):
        error_dict = dict(self.payload) if self.payload else {}
        error_dict['message'] = self.message

        return error_dict


class DatabaseError(SQLAlchemyError):
    pass
