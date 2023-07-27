import requests, json, datetime
from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('clicksend')


def make_api_call(method="GET", endpoint="", config=None, params=None, data=None, json_data=None):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        server_url = config.get('url').strip('/')
        if not server_url.startswith('https://') and not server_url.startswith('http://'):
            server_url = "https://" + server_url
        server_url = server_url + endpoint
        response = requests.request(method=method, auth=(config.get('username'), config.get('password')),
                                    url=server_url,
                                    headers=headers, data=data, json=json_data, params=params,
                                    verify=config.get('verify_ssl'))
        if response.ok:
            return response.json()
        else:
            if response.text != "":
                err_resp = response.json()
                failure_msg = err_resp['response_msg']
                error_msg = 'Response [{0}:{1} Details: {2}]'.format(response.status_code, response.reason,
                                                                     failure_msg if failure_msg else '')
            else:
                error_msg = 'Response [{0}:{1}]'.format(response.status_code, response.reason)
            logger.error(error_msg)
            raise ConnectorError(error_msg)
    except requests.exceptions.SSLError:
        logger.error('An SSL error occurred')
        raise ConnectorError('An SSL error occurred')
    except requests.exceptions.ConnectionError:
        logger.error('A connection error occurred')
        raise ConnectorError('A connection error occurred')
    except requests.exceptions.Timeout:
        logger.error('The request timed out')
        raise ConnectorError('The request timed out')
    except requests.exceptions.RequestException:
        logger.error('There was an error while handling the request')
        raise ConnectorError('There was an error while handling the request')
    except Exception as err:
        raise ConnectorError(str(err))


def convert_to_epoch(time):
    datetime_obj = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
    return int(datetime_obj.timestamp())


def build_payload(params):
    params.pop('send_to', '')
    data = {"source": "python"}
    for k, v in params.items():
        if v or v is False:
            if k == "schedule":
                data[k] = convert_to_epoch(params.get("schedule"))
            elif k == "require_input" or k == "machine_detection":
                data[k] = 1 if v else 0
            else:
                data[k] = v
    return data


def send_message(config, params):
    payload = {"messages": [build_payload(params)]}
    logger.error('payload is -----> {}'.format(payload))
    endpoint = "/v3/sms/send"
    return make_api_call(method='POST', endpoint=endpoint, data=json.dumps(payload), config=config)


def get_contact_list(config, params):
    endpoint = "/v3/lists"
    return make_api_call(endpoint=endpoint, params=build_payload(params), config=config)


def send_voice_message(config, params):
    payload = {"messages": [build_payload(params)]}
    payload['messages'][0]['voice'] = payload['messages'][0]['voice'].lower()
    logger.error('payload is -----> {}'.format(payload))
    endpoint = "/v3/voice/send"
    return make_api_call(method='POST', endpoint=endpoint, data=json.dumps(payload), config=config)


def _check_health(config):
    try:
        get_contact_list(config, params={})
        return True
    except Exception as e:
        logger.error("Invalid Credentials: %s" % str(e))
        raise ConnectorError("Invalid Credentials")


operations = {
    'send_message': send_message,
    'get_contact_list': get_contact_list,
    'send_voice_message': send_voice_message
}
