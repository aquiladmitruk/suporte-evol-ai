import urllib.request, json, ssl

base = 'https://df83cbbd-a7c2-4311-b432-0b9ad8d14eb9.sa-east-1-0.aws.cloud.qdrant.io'
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6ZWJmZDhkMzUtOTRlYS00MGM3LWJiNTEtNTA4MTQ4YWU1MDZmIn0.Nbr9CA52buMBv_lV_JkYErUo6kQhfi8f75bQdEqink4'
ctx = ssl.create_default_context()

body = json.dumps({'limit': 3, 'with_payload': True, 'with_vectors': False}).encode()
req = urllib.request.Request(
    base + '/collections/documents/points/scroll',
    data=body,
    headers={'api-key': token, 'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req, context=ctx) as resp:
    data = json.loads(resp.read())
    for p in data['result']['points']:
        print(json.dumps(p['payload'], indent=2))
        print('---')
