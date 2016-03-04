#!/usr/bin/env python
# coding: utf-8

import json, requests

def passage_as_dict(ref, version='nasb'):
    '''getbible.net does not valid json so we convert (content); to [content]'''
    fmt = 'https://getbible.net/json?p={}&v={}'
    url = fmt.format(ref.replace(' ', '%20'), version)
    return json.loads('[{}]'.format(requests.get(url).text[1:-2]))

def passages_as_dicts(ref, version='nasb'):
    return [passage_as_dict(p.strip(), version)
            for p in ref.split(';') if p.strip()]

# Matthew is 'type': 'book', Mark is 'type': 'chapter', Luke and John are 'type': 'verse'
passages = passages_as_dicts('Matthew;Mark 1;Luke 1:1;John 1:1-3')
print(json.dumps(passages, indent=4, sort_keys=True))
