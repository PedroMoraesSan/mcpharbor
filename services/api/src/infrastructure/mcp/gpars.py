from shared.errors import AUTHORIZATION_DENIED, AUTHORIZATION_DENIED_CODE, SERVER_UNAVAILABLE, SERVER_UNAVAILABLE_CODE

JSONRPC_VERSION = "2.0"


def authorization_denied(req_id: int | str | None, detail: str) -> dict:
    return {
        "jsonrpc": JSONRPC_VERSION,
        "id": req_id,
        "error": {
            "code": AUTHORIZATION_DENIED_CODE,
            "message": detail,
            "data": {"gpars_code": AUTHORIZATION_DENIED},
        },
    }


def server_unavailable(req_id: int | str | None, detail: str) -> dict:
    return {
        "jsonrpc": JSONRPC_VERSION,
        "id": req_id,
        "error": {
            "code": SERVER_UNAVAILABLE_CODE,
            "message": detail,
            "data": {"gpars_code": SERVER_UNAVAILABLE},
        },
    }
