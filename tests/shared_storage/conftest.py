import shutil
import subprocess

import pytest


@pytest.fixture(scope="session")
def make_cert(tmp_path_factory):
    """Make a self-signed certificate: returns (cert path, key path)."""
    openssl = shutil.which("openssl")
    if openssl is None:
        pytest.skip("openssl is needed to make test certificates")
    folder = tmp_path_factory.mktemp("tls")

    def run(*args):
        subprocess.run([str(openssl), *map(str, args)], check=True, capture_output=True)

    def make(name="replica", signed_by=None, extra=()):
        """``signed_by``: the (cert, key) of a CA to sign with, instead of
        signing it with its own key. ``extra``: more ``openssl req`` options
        for a self-signed one."""
        cert, key = folder / f"{name}.pem", folder / f"{name}.key"
        if cert.exists():
            return str(cert), str(key)
        newkey = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:prime256v1"]
        if "-passout" not in extra:
            newkey.append("-nodes")
        subject = ["-subj", f"/CN={name}", "-keyout", key]
        if signed_by is None:
            run("req", "-x509", *newkey, "-days", "2", *subject, *extra, "-out", cert)
        else:
            csr = folder / f"{name}.csr"
            run("req", "-new", *newkey, *subject, "-out", csr)
            ca_cert, ca_key = signed_by
            run(
                "x509", "-req", "-in", csr, "-CA", ca_cert, "-CAkey", ca_key,
                "-CAcreateserial", "-days", "2", "-out", cert,
            )  # fmt: skip
        return str(cert), str(key)

    return make
