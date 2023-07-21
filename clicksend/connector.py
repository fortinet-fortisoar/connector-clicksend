from connectors.core.connector import Connector
from connectors.core.connector import get_logger, ConnectorError
from .operations import operations
from django.core.mail import send_mail, get_connection

logger = get_logger('clicksend')


class Clicksend(Connector):

    def on_add_config(self, config, active):
        try:
            tokens = operations._get_access_token(config)
            config["access_token"] = tokens["access_token"]
            config["refresh_token"] = tokens["refresh_token"]
        except Exception as e:
            error_message = "Error setting access and refresh tokens. Error message as follows:\n{}".format(str(e))
            logger.exception(error_message)
            raise ConnectorError(error_message)

    def execute(self, config, operation, params, **kwargs):
        try:
            action = operations.get(operation)
            result = {}

            result = action(config, params)
            return result
        except Exception as e:
            error_message = "Error in execute function. Error message as follows:\n{}".format(str(e))
            raise ConnectorError(error_message)


    def check_health(self, config):
        try:
            return operations.get("check_health")(config)
        except Exception as e:
            error_message = "Error in health check. Error message as follows:\n{}".format(str(e))
            raise ConnectorError(error_message)
