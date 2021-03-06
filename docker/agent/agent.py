#!/usr/bin/env python3

from flask import Flask, Response, redirect, stream_with_context
from flask_restful import Resource, Api, reqparse
from ipfsapi import connect
from json import dumps
from os import environ
import requests

app = Flask(__name__)
api = Api(app)

@app.route('/')
def index():
    return redirect('/ipns/{0}/'.format(environ['DAPP_IPNS']))

@app.route('/ipns/<path:url>')
def dapp(url):
    dapp_url = 'http://{0}/ipns/{1}'.format(environ['IPFS_NODE'], url)
    req = requests.get(dapp_url, stream = True)
    return Response(stream_with_context(req.iter_content()),
                    content_type = req.headers['content-type'])

class Descriptor(Resource):
    def get(self):
        ipfs = connect(environ['IPFS_NODE'], 5001)

        desc = {}
        desc['IPNS'] = ipfs.id()['ID']
        desc['address'] = open('/chain/address.txt', 'r').readline()[:-1]

        return {'descriptor': ipfs.add_json(desc)}

class Market(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('market')
        self.parser.add_argument('beneficiary')
        self.parser.add_argument('bid')
        self.parser.add_argument('ask')

    def get(self):
        try:
            return loads(open('/conf/market.json', 'r').readall())
        except:
            return {}

    def post(self):
        args = self.parser.parse_args()
        open('/conf/market.json', 'w').write(dumps(args))
        return {'success':'ok'}

api.add_resource(Descriptor, '/api/v1/descriptor')
api.add_resource(Market,     '/api/v1/market')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
