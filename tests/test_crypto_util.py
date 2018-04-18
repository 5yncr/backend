import asyncio
import os

from syncr_backend.util import crypto_util


def test_encode_frozenset_bad_input() -> None:
    f = os.urandom(12)
    fs = crypto_util.encode_frozenset_prefix + f
    decoded_frozenset = crypto_util.decode_peerlist_frozenset(f)
    decoded_frozenset2 = crypto_util.decode_peerlist_frozenset(fs)
    assert decoded_frozenset is None and decoded_frozenset2 is None


def test_encode_peerlist_frozenset() -> None:

    f = frozenset([('12', 123, '1234'), ('asdf', 123, 'asdf'), ])
    ef = crypto_util.encode_peerlist_frozenset(f)
    df = crypto_util.decode_peerlist_frozenset(ef)
    assert f == df


def test_signature() -> None:
    loop = asyncio.get_event_loop()
    rsa_private_key = loop.run_until_complete(
        crypto_util.generate_private_key(),
    )
    d = {
        'a': 1,
        'b': 2,
        'c': 3,
    }
    signature = loop.run_until_complete(
        crypto_util.sign_dictionary(rsa_private_key, d),
    )
    loop.run_until_complete(crypto_util.verify_signed_dictionary(
        rsa_private_key.public_key(),
        signature,
        d,
    ))
