import json, requests

def passage_as_dict(ref, version):
    '''getbible.net does not valid json so we convert (content); to [content]'''
    fmt = 'https://getbible.net/json?p={}&v={}'
    url = fmt.format(ref.replace(' ', '%20'), version)
    return json.loads('[{}]'.format(requests.get(url).text[1:-2]))

print(passage_as_dict('Luke 3:1', 'nasb'))
