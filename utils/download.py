import requests
import cbor

from utils.response import Response


def download(url, config, logger=None):
    host, port = config.cache_server

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


def prep_download(url, config, logger=None) -> bool:
    """
    Determines if the url should be downloaded by the requesting the headers instead of the full content. It grabs the content-length.
    Returns True if we should download.
    Returns False if file size is greater than file size initialized in config.
    """
    host, port = config.cache_server

    resp = requests.head(
        f"http://{host}:{port}/", params=[("q", f"{url}"), ("u", f"{config.user_agent}")]
    )

    content_length = resp.headers.get("Content-Length")
    if content_length is not None:
        size = int(content_length)
        if size > config.max_file_size * 1048576:
            if logger:
                logger.info(
                    f"Skipping {url}. File size threshold exceeded {config.max_file_size * 1048576} with {size}"
                )
            return False
    return True
