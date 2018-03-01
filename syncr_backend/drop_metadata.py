from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import bencode  # type: ignore

from syncr_backend import crypto_util


class DropVersion(object):

    def __init__(self, version: bytes, nonce: bytes) -> None:
        self.version = version
        self.nonce = nonce

    def __iter__(self):
        yield 'version', self.version
        yield 'nonce', self.nonce


class DropMetadata(object):

    def __init__(
        self, drop_id: bytes, name: str, version: DropVersion,
        previous_versions: List[DropVersion], primary_owner: bytes,
        other_owners: Dict[bytes, int], signed_by: bytes,
        files: Dict[str, bytes], files_hash: Optional[bytes]=None,
        sig: Optional[bytes]=None, protocol_version: int=1,
    ) -> None:
        self.id = drop_id
        self.name = name
        self.version = version
        self.previous_versions = previous_versions
        self.owner = primary_owner
        self.other_owners = other_owners
        self.signed_by = signed_by
        self.files = files
        self.sig = sig
        self._protocol_version = protocol_version
        self._files_hash = files_hash

    def add_key(self, key: crypto_util.rsa.RSAPrivateKey) -> None:
        self._priv_key = key
        self._pub_key = key.public_key()

    def add_pub_key(self, key: crypto_util.rsa.RSAPrivateKey) -> None:
        self._pub_key = key

    @property
    def files_hash(self) -> bytes:
        if self._files_hash is not None:
            return self._files_hash
        else:
            return self.gen_files_hash()

    def gen_files_hash(self) -> bytes:
        return crypto_util.hash(bencode.encoded(self.files))

    def verify_files_hash(self) -> None:
        if self._files_hash is None:
            raise Exception("Invalid files hash")
        given = self._files_hash
        expected = self.gen_files_hash()
        if given != expected:
            raise Exception("Invalid files hash")

    @property
    def unsigned_header(self) -> Dict[str, Any]:  # TODO: type this better?
        h = {
            "protocol_version": self._protocol_version,
            "drop_id": self.id,
            "name": self.name,
            "version": self.version.version,
            "version_nonce": self.version.nonce,
            "previous_version": [dict(v) for v in self.previous_versions],
            "primary_owner": self.owner,
            "other_owners": self.other_owners,
            "header_signature": b"",
            "signed_by": self.signed_by,
            "files_hash": self.files_hash,
            "files": [],
        }
        return h

    @property
    def header(self) -> Dict[str, Any]:
        h = self.unsigned_header
        key = get_priv_key(self.signed_by)
        h_sig = crypto_util.sign_dictionary(key, h)
        h["header_signature"] = h_sig
        return h

    def verify_header(self) -> None:
        if self.sig is None:
            raise Exception("Invalid signature")
        key = get_priv_key(self.signed_by)
        crypto_util.verify_signed_dictionary(
            key, self.sig, self.unsigned_header,
        )

    def encode(self) -> bytes:
        h = self.header
        h["files"] = self.files
        return bencode.encode(h)

    @staticmethod
    def decode(b: bytes) -> 'DropMetadata':
        # Note: assumes signed header
        decoded = bencode.decode(b)
        dm = DropMetadata(
            drop_id=decoded["drop_id"],
            name=decoded["name"],
            version=DropVersion(decoded["version"], decoded["version_nonce"]),
            previous_versions=[
                DropVersion(
                    v["version"],
                    v["version_nonce"],
                ) for v in decoded["previous_versions"]
            ],
            primary_owner=decoded["primary_owner"],
            other_owners=decoded["other_owners"],
            signed_by=decoded["signed_by"],
            files_hash=decoded["files_hash"],
            files=decoded["files"],
            sig=decoded["header_signature"],
        )
        dm.verify_files_hash()
        dm.add_pub_key(get_pub_key(dm.signed_by))
        dm.verify_header()
        return dm


def get_pub_key(nodeid: bytes) -> crypto_util.rsa.RSAPublicKey:
    raise NotImplementedError()


def get_priv_key(nodeid: bytes) -> crypto_util.rsa.RSAPrivateKey:
    raise NotImplementedError()
