import requests
import cbor
import time

from utils.response import Response


def download(url, config, logger=None, delay: int = 0):
    host, port = config.cache_server

    if not delay:
        delay = 0

    time.sleep(delay)

    resp = requests.get(
        f"http://{host}:{port}/", params=[("q", f"{url}"), ("u", f"{config.user_agent}")]
    )
    try:
        if resp and resp.content and resp.headers:
            return Response(cbor.loads(resp.content), headers=resp.headers)
    except (EOFError, ValueError) as e:
        pass
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response(
        {
            "error": f"Spacetime Response error {resp} with url {url}.",
            "status": resp.status_code,
            "url": url,
        },
        None,
    )
