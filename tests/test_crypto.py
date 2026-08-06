import unittest
from unittest.mock import patch

from Classes.Crypto import Crypto, Nonce


class CryptoTests(unittest.TestCase):
    def test_post_login_decrypt_removes_secretbox_zero_prefix(self):
        crypto = Crypto()
        crypto.decryptNonce = Nonce(bytes(24))

        def fake_open(output, payload, length, nonce, key):
            output[:] = bytes(32) + b"laser"

        with patch(
            "Classes.Crypto.crypto_secretbox_xsalsa20poly1305_tweet_open",
            side_effect=fake_open,
        ):
            self.assertEqual(b"laser", crypto.decryptClient(14102, bytes(21)))


if __name__ == "__main__":
    unittest.main()
