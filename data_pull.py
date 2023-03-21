import time
import asyncio
import aiohttp
import nest_asyncio
import ssl
import socket
import certifi
# import os
from async_retrying import retry
from .pkcs12_handler import pfx_to_pem
import pdb

nest_asyncio.apply()
durations = []
server_response_errors = 0
timeout_errors = 0


def timed(func):
    """
    records approximate durations of function calls
    """

    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = f"finished in {time.time() - start:.2f} seconds"
        durations.append(duration)
        return result

    return wrapper


@retry(attempts=15)
async def fetch(self, url, session, get=False, post=False, post_json={}):
    """
    asynchronous get request

    Parameters
    ----------
    url : str
      URL to make call to
    session : object
      Session object
    get : bool
      Set to perform get request
    post : bool
      Set to perform post request
    post_json : dict
      Dict to use with post request
    Returns
    -------
    response_json : dict
      JSON dictionary response
    """
    global server_response_errors
    global timeout_errors

    try:
        if get:
            async with session.get(url, timeout=None) as response:
                if response.ok:
                    response_json = await response.json()
                    if hasattr(self, "progressBar"):
                        self.progressBar.update(1)
                    return response_json
                else:
                    time.sleep(1)
                    server_response_errors += 1
                    if server_response_errors > 3:
                        print(
                            """/nToo many server response errors occurred.
                             Please restart your Kenrel and try again.
                             If the problem persists contact your developer."""
                        )
                    else:
                        await fetch(self, url, session, get=True)
        elif post:
            async with session.post(
                url, timeout=None, json=post_json, raise_for_status=True
            ) as response:
                if response.ok:
                    response_json = await response.json()
                    if hasattr(self, "progressBar"):
                        self.progressBar.update(1)
                    return response_json
    except asyncio.TimeoutError:
        print(
            """/nToo many server response errors occurred.
               Please restart your Kenrel and try again.
               If the problem persists contact your developer."""
        )


async def fetch_many(
        self, loop, urls, cert, get=False, post=False, post_jsons=[{}]):
    """
    many asynchronous get requests, gathered

    Parameters
    ----------
    loop : obj
      asyncio.get_event_loop() object
    urls : [str]
      List of URLs to create session.get() tasks with
    cert : str
      filepath for certificate
    get : bool
      Set to perform get request
    post : bool
      Set to perform post request
    post_jsons : [dict]
      list of dictionaries to use with post requests
    Returns
    -------
    asyncio.gather(*tasks) : obj
      Response object
    """

    with pfx_to_pem(cert, self.pw) as cert:
        sslcontext = ssl.create_default_context(cafile=certifi.where())
        sslcontext.load_cert_chain(certfile=cert)

        conn = aiohttp.TCPConnector(
            ssl_context=sslcontext, family=socket.AF_INET,
            limit=100, limit_per_host=0
        )
        if get:
            async with aiohttp.ClientSession(connector=conn) as session:
                tasks = [loop.create_task(fetch(self, url, session, get=True))
                         for url in urls]
                return await asyncio.gather(*tasks)
        elif post:
            async with aiohttp.ClientSession(connector=conn) as session:
                tasks = [
                    loop.create_task(
                        fetch(self, urls[0], session, post=True,
                              post_json=post_json))
                    for post_json in post_jsons
                ]
                return await asyncio.gather(*tasks)


@timed
def sync_requests_get_all(urls, session):
    """
    performs syncronous get requests
    Parameters
    ----------
    urls : [str]
      List of URLs to create session.get() tasks with
    session : obj
      Session object to make session.get()
    Returns
    -------
    json : {}
      JSON dictionary response
  """
    return [session.get(url).json() for url in urls]


@timed
def async_requests_get_all(urls, session):
    """
    asynchronous wrapper around synchronous requests
    Parameters
    ----------
    urls : [str]
      List of URLs to create session.get() tasks with
    session : obj
      Session object to make session.get()
    Returns
    -------
    loop.run_until_complete(asyncio.gather(*tasks)) : obj
      Response object
    """
    loop = asyncio.get_event_loop()
    # use session to reduce network overhead

    async def async_get(url):
        return session.get(url)

    async_tasks = [loop.create_trask(async_get(url)) for url in urls]
    return loop.run_until_complete(asyncio.gather(*async_tasks))


@timed
def async_aiohttp_get_all(
        self, urls, cert, get=False, post=False, post_jsons=[{}]):
    """
    asynchronous requests

    Parameters
    ----------
    urls : [str]
      List of URLs to create session.get() tasks with
    cert : str
      filepath for certificate
    get : bool
      Set to perform get request
    post : bool
      Set to perform post request
    post_jsons : [dict]
      list of dictionaries to use with post requests
    Returns
    -------
    resp : obj
      Response object
    """
    global server_response_errors
    server_response_errors = 0
    loop = asyncio.get_event_loop()
    if get:
        resp = loop.run_until_complete(
            fetch_many(self, loop, urls, cert, get=True))
    elif post:
        resp = loop.run_until_complete(fetch_many(
            self, loop, urls, cert, post=True, post_jsons=post_jsons))
    return resp, durations


"""
import data_pull
from session import Session, get_cert_location
"""
