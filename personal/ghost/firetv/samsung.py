"""Samsung Tizen TV remote over its local API (port 8002). Stdlib only.
Usage: python -I samsung.py info | keys | key <name|KEY_*> ...
TV IP from ~/.claude/firetv.json ("tv"). Pairing token kept locally in ~/.claude/samsung-token.txt (never in repo).
"""
import base64, json, os, socket, ssl, struct, sys, time, urllib.request

HOME = os.path.expanduser('~/.claude')
TOK = os.path.join(HOME, 'samsung-token.txt')
ALIAS = dict(power='KEY_POWER', volup='KEY_VOLUP', voldown='KEY_VOLDOWN', mute='KEY_MUTE', source='KEY_SOURCE',
             hdmi='KEY_HDMI', hdmi1='KEY_HDMI1', hdmi2='KEY_HDMI2', hdmi3='KEY_HDMI3', home='KEY_HOME',
             back='KEY_RETURN', up='KEY_UP', down='KEY_DOWN', left='KEY_LEFT', right='KEY_RIGHT', ok='KEY_ENTER',
             menu='KEY_MENU', exit='KEY_EXIT', info='KEY_INFO', play='KEY_PLAY', pause='KEY_PAUSE')


def tv_ip():
    ip = json.load(open(os.path.join(HOME, 'firetv.json'), encoding='utf-8-sig')).get('tv')
    if not ip:
        sys.exit('No TV IP: firetv.ps1 set <stickIP> <tvIP>')
    return ip


def frame(text):  # client frames must be masked
    data, mask = text.encode(), os.urandom(4)
    n = len(data)
    head = b'\x81' + (bytes([0x80 | n]) if n < 126 else bytes([0xFE]) + struct.pack('>H', n))
    return head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data))


def connect(ip):
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE  # self-signed TV cert
    s = ctx.wrap_socket(socket.create_connection((ip, 8002), timeout=40))
    tok = open(TOK).read().strip() if os.path.exists(TOK) else ''
    path = '/api/v2/channels/samsung.remote.control?name=' + base64.b64encode(b'ClaudeRemote').decode() + (f'&token={tok}' if tok else '')
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(f'GET {path} HTTP/1.1\r\nHost: {ip}:8002\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
              f'Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n'.encode())
    data = b''
    try:
        while b'ms.channel' not in data:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        sys.exit('No reply: choose Allow on the TV prompt, then rerun')
    if b'ms.channel.connect' not in data:
        sys.exit('TV refused: re-allow in TV Settings > General > External Device Manager > Device Connection Manager > Device List')
    body = data[data.index(b'{'):]
    try:
        new = json.loads(body.split(b'\n')[0]).get('data', {}).get('token')
        if new:
            open(TOK, 'w').write(new)
    except ValueError:
        pass
    return s


def main(argv):
    act = argv[0] if argv else 'info'
    if act == 'keys':
        for k, v in sorted(ALIAS.items()):
            print(f'{k} = {v}')
    elif act == 'info':
        d = json.load(urllib.request.urlopen(f'http://{tv_ip()}:8001/api/v2/', timeout=5))['device']
        for k in ('name', 'modelName', 'PowerState', 'networkType'):
            print(f'{k}: {d.get(k)}')
    elif act == 'key':
        s = connect(tv_ip())
        for k in argv[1:]:
            key = ALIAS.get(k) or (k if k.startswith('KEY_') else 'KEY_' + k.upper())
            msg = {'method': 'ms.remote.control', 'params': {'Cmd': 'Click', 'DataOfCmd': key, 'Option': 'false', 'TypeOfRemote': 'SendRemoteKey'}}
            s.sendall(frame(json.dumps(msg))); time.sleep(0.4); print('sent', key)
        s.close()
    else:
        print('actions: info keys key <name|KEY_*>...')


if __name__ == '__main__':
    main(sys.argv[1:])
