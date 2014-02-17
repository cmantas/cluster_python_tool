__author__ = 'cmantas'

from kamaki.clients import ClientError
#from astakosclient import AstakosClient #not working fuck yeah
# okeanos bullshit
from kamaki.clients.astakos import CachedAstakosClient as AstakosClient

from kamaki.clients.cyclades import CycladesClient, CycladesNetworkClient
#http://www.synnefo.org/docs/kamaki/latest/developers/code.html#the-client-api-ref
from sys import stderr
from os.path import abspath,exists
from os import mkdir
from base64 import b64encode
from persistance_module import *

USER = "cmantas"

#retrieve the credentials for the specified users
AUTHENTICATION_URL, TOKEN = get_credentials(USER)
synnefo_user = AstakosClient(AUTHENTICATION_URL, TOKEN)
cyclades_endpoints = synnefo_user.get_service_endpoints("compute")
CYCLADES_URL = cyclades_endpoints['publicURL']
cyclades_client = CycladesClient(CYCLADES_URL, TOKEN)
cyclades_net_client = CycladesNetworkClient(CYCLADES_URL, TOKEN)


pub_keys_path = 'keys/just_a_key.pub'
priv_keys_path = 'keys/just_a_key'


#creates a "personality"
def personality():
    """
    :param pub_keys_path: a path to the public key(s) to be used for this personality
    :param ssh_keys_path: a path to the private key(s) to be used for this personality
    """
    personality = []
    # if ssh_keys_path:
        # with open(abspath(ssh_keys_path)) as f:
        #     personality.append(dict(
        #         contents=b64encode(f.read()),
        #         path='/root/.ssh/id_rsa',
        #         owner='root', group='root', mode=0600))
    if pub_keys_path:
        with open(abspath(pub_keys_path)) as f:
            personality.append(dict(
                contents=b64encode(f.read()),
                path='/root/.ssh/authorized_keys',
                owner='root', group='root', mode=0600))
            personality.append(dict(
                contents=b64encode(f.read()),
                path='/user/.ssh/authorized_keys',
                owner='user', group='user', mode=0600))
    if priv_keys_path or pub_keys_path:
            personality.append(dict(
                contents=b64encode('StrictHostKeyChecking no'),
                path='/root/.ssh/config',
                owner='root', group='root', mode=0600))
            personality.append(dict(
                contents=b64encode('StrictHostKeyChecking no'),
                path='/user/.ssh/config',
                owner='user', group='user', mode=0600))
    return personality









