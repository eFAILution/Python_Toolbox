from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile
from cryoptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryoptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates
)


@contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    """
    Decrypts the .pfx file to be used with requests

    Parameters
    ----------
    pfx_path : str
      filepath of certificate
    pfx_password : str
      password to unlock file

    Returns
    -------
    None
    """
    pfx = Path(pfx_path).read_bytes()
    private_key, main_cert, add_certs = load_key_and_certificates(
        pfx, pfx_password.encode("utf-8"), None
    )

    with NamedTemporaryFile(suffix=".pem") as t_pem:
        with open(t_pem.name, "wb") as pem_file:
            pem_file.write(
                private_key.private_bytes(
                    Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
                )
            )
            pem_file.write(main_cert.public_bytes(Encoding.PEM))
            for ca in add_certs:
                pem_file.write(ca.public_bytes(Encoding.PEM))
            yield t_pem.name


"""
How to use:
with pfx_to_pem('foo.p12', 'foo_password') as cert:
  resp = requests.post(url, cert=cert, data=payload)
"""
