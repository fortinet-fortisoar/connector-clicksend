import time, requests, json, base64, datetime
from connectors.core.connector import get_logger, ConnectorError, _api_call

logger = get_logger('clicksend')


def send_message(config, params):
    try:
        to = params.get("to")
        message = params.get("message")
        schedule = time.mktime(datetime.datetime.strptime(params.get("schedule"), '%Y-%m-%dT%H:%M:%S.0Z'))
        from_number = params.get("from_number")

        credentials = "{0}:{1}".format(config["username"], config["password"])
        encoded_creds = base64.b64encode(bytes(credentials))
        headers = {"Authorization": "Basic {0}".format(encoded_creds),
                   "Content-Type": "application/json"}
        url = "{0}/v3/sms/send".format(config.get("url"))

        body = {"messages":
            [{
                "source": "python",
                "from": from_number,
                "to": to,
                "body": message,
                "schedule": schedule
            }]
        }
        response = _api_call(url,
                             headers=headers,
                             method='POST',
                             body=body)
        return response

    except Exception as e:
        error_message = "Error sending message. Error message as follows:\n{}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


def check_health(config):
    logger.info("health check started")
    try:
        url = "{0}/v3/automations/sms/inbound".format(config.get("url"))
        headers = {"Content-Type": "application/json"}
        _api_call(url, headers=headers)
        return True
    except Exception as e:
        error_message = "Error in health check. Error message as follows:\n{}".format(str(e))
        logger.exception(error_message)
        raise ConnectorError(error_message)


operations = {
    'send_message': send_message,
    'check_health': check_health
}
