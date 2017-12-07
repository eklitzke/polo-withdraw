# Copyright (c) 2017 Evan Klitzke <evan@eklitzke.org>
#
# This file is part of polo-withdraw.
#
# polo-withdraw is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# polo-withdraw is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# polo-withdraw. If not, see <http://www.gnu.org/licenses/>.

import argparse
import poloniex
import json
import urllib.request
from bitcoinrpc.authproxy import AuthServiceProxy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', help='key')
    parser.add_argument('-s', '--secret', help='secret key')
    parser.add_argument('-r', '--rpcauth', help='user:password')
    parser.add_argument(
        '-l',
        '--withdrawal-limit',
        type=int,
        default=25000,
        help='Poloniex withdrawal limit')
    parser.add_argument('--no-segwit', default=False, action='store_true')
    parser.add_argument(
        '--max-tries', type=int, default=10, help='time to retry')
    args = parser.parse_args()

    if not (args.key and args.secret and args.rpcauth):
        parser.error('must pass -k and -s and -r')

    polo = poloniex.Poloniex(key=args.key, secret=args.secret)
    btc_balance = float(polo.returnBalances()['BTC'])

    with urllib.request.urlopen(
            'https://api.coindesk.com/v1/bpi/currentprice.json') as response:
        data = json.loads(response.read())
        usd_rate = data['bpi']['USD']['rate_float']

    max_withdrawal = args.withdrawal_limit / usd_rate
    withdraw_amt = min(max_withdrawal, btc_balance)

    rpc_conn = AuthServiceProxy('http://{}@127.0.0.1:8332'.format(
        args.rpcauth))

    addr = rpc_conn.getnewaddress()
    if not args.no_segwit:
        addr = rpc_conn.addwitnessaddress(addr)

    for x in range(args.max_tries):
        try:
            print('BTC {} {}'.format(withdraw_amt, addr))
            print(polo.withdraw('BTC', withdraw_amt, addr))
            break
        except poloniex.PoloniexError:
            withdraw_amt *= 0.9
