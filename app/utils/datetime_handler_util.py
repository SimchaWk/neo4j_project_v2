from neo4j.time import DateTime


def format_neo4j_datetime(obj):
    if isinstance(obj, DateTime):
        return obj.isoformat()
    return obj


def format_response_datetime(response: dict) -> dict:
    if isinstance(response, dict):
        return {k: format_response_datetime(v) for k, v in response.items()}
    elif isinstance(response, list):
        return [format_response_datetime(item) for item in response]
    elif isinstance(response, DateTime):
        return format_neo4j_datetime(response)
    return response
