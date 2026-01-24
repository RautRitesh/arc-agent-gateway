# Copyright (c) 2023, Circle Technologies, LLC. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import codecs
# Installed by `pip install pycryptodome`
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256

# Paste your entity public key here.
public_key_string = "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAmi9EJD1zBYfcT4OCHiSC\nZr9eLW1X5oY+oK9NzIG17ewgnGv9SjvcpUwOWxMUs30ebL6zjqKSfqaFW49JTGA1\nXElYMHIPVUMJjxTJhXsOAWIVs24/zzP1ySQwHMpj3o0IZEO193x8rIFivKx6W81C\n3ZmV/AzR10Z1IM6UGaQLHNIiTFz5SMbaAEA/MF9io0+5loIFjvTYs4nbjqXxKXPJ\nd7CeHT/6+4Ozwb3N7LDX7TxiD2UGyfYnn3bLxKmjvSQciYPUthDDJsJg9BuaVzVG\n2a0C7GlCkTankLmdPTYDejTNpFQwm1teebnvi1UxBcVjv/BVtT2S8DVRCJQJJp4s\ndxZ7PwdqBtb82+HBsYjonQdFlosvLUH3ZITBjOKDMMhNPd0nqgeabmEERcwhGhsJ\ng1bFxdwyKrcWcjIN9hVIOV9uYUkcXArbVCePYSKC1+mRRtl2fZ6UtIhKG6So5P+R\nsWEVb9q2vYKLtJ/X6vTtMn1k09u1+wnx6OreFZ+lq3+QwZw2l6AWR3by1yX7O1Jb\nyxn1RI0mlXvnn+N/hBGL8bTf70/lKbZh+Bf4GB6jK3u529R0i471WU8whYYMGfMS\nZyGQLeskvhaIg6celP6lXT4i3yobgcdCt4K1rLearotakr9oofxVdzgU7Tsll7zy\nSGny6E5Ek+xq9ux4Ufj8/Y0CAwEAAQ==\n-----END PUBLIC KEY-----\n"

# If you already have a hex encoded entity secret, you can paste it here. the length of the hex string should be 64.
hex_encoded_entity_secret = '1dbae7af1c5061dc794c538859b1f637cb3b10670b3ae9a89c11d6241e9a84e9'

# The following sample codes generate a distinct entity secret ciphertext with each execution.
if __name__ == '__main__':
    entity_secret = bytes.fromhex(hex_encoded_entity_secret)

    if len(entity_secret) != 32:
        print("invalid entity secret")
        exit(1)

    public_key = RSA.importKey(public_key_string)

    # encrypt data by the public key
    cipher_rsa = PKCS1_OAEP.new(key=public_key, hashAlgo=SHA256)
    encrypted_data = cipher_rsa.encrypt(entity_secret)

    # encode to base64
    encrypted_data_base64 = base64.b64encode(encrypted_data)

    print("Hex encoded entity secret:", codecs.encode(entity_secret, 'hex').decode())
    print("Entity secret ciphertext:", encrypted_data_base64.decode())
