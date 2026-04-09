import requests


def msg(web_session):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://www.xiaohongshu.com",
        "priority": "u=1, i",
        "referer": "https://www.xiaohongshu.com/",
        "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "x-b3-traceid": "60c4ccacef9d7b02",
        "x-s": "XYS_2UQhPsHCH0c1PUhAHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlLSQc/oGlpLYEaDEbqemk8rkayrTEp9+awepnJf4x2bSiwrDUy0mP+FDF8o8O8o+oqBRawsRnLgSIpnbsweH3GDRAcdbOJDEEnaVEzSZELS+h/F8+J9RO/MpG4DR6/dDFadS3PDbearlT/MYPJp8mPrkHaMY/+FTpznbTPB8+c9EIqMQCLDkcpnbLP9le8LT/Jfznnfl0yFLIaSQQyAmOarEaLSz+GURDpD+daBbUzgkmyBSm+A88+rHEPsHVHdWFH0ijHdF=",
        "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1PUhAHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjH9N0c1PaHVHdWMH0ijP/DEG9Lh8/DAG0Q3q0P9G/S6qdilwoYk+oWA4AYi80m0G9R7+fWEy7iMPeZIPePEwer7+jHVHdW9H0ijHjIj2eqjwjHjNsQhwsHCHDDAwoQH8B4AyfRI8FS98g+Dpd4daLP3JFSb/BMsn0pSPM87nrldzSzQ2bPAGdb7zgQB8nph8emSy9E0cgk+zSS1qgzianYt8Lzf/LzN4gzaa/+NqMS6qS4HLozoqfQnPbZEp98QyaRSp9P98pSl4oSzcgmca/P78nTTL08z/sVManD9q9z1J9p/8db8aob7JeQl4epsPrz6agW3Lr4ryaRApdz3agYDq7YM47HFqgzkanYMGLSbP9LA/bGIa/+nprSe+9LI4gzVPDbrJg+P4fprLFTALMm7+LSb4d+kpdzt/7b7wrQM498cqBzSpr8g/FSh+bzQygL9nSm7qSmM4epQ4flY/BQdqA+l4oYQ2BpAPp87arS34nMQyF8E8nkdqMD6pMzd8/4SL7bF8aRr+7+rG7mkqBpD8pSUzozQcA8Szb87PDSb/d+/qgzVJfl/4LExpdzQ4fRSy7bFP9+y+7+nJAzdaLp/2LSiz/Qz8dbMagYiJdbCwB4QyFSfJ7b7yFSenS4oJA+A8BlO8p8c4A+Q4DbSPB8d8nz/zBEQye4A2BrF/g4M4epQzLTApBRm8nz+a7PApd4C8n8d8Lzl4opQ2BSTGSpDq9zM4rpAq94SngbFJFS9yLRQc7rlq7pFqrQn4FRd+AYS49+N8pP7+npLpd4CanSO8/ZEcnLAp9laanYD8p+V+dP9JMzVanW9q9zl4AmQznQnwopFPd4c4e+Q2BpApDDROaHVHdWEH0iTP0ZMPeqI+0Z9wsIj2erIH0iINsQhP/rjwjQ1J7QTGnIjNsQhP/HjwjHl+AqM+0HEPeLEPAZ7wAr7+AcFP0qI+AcIPePjKc==",
        "x-t": "1775629059902",
        "x-xray-traceid": "ceb5dea37ee3f2842e73479f645a6f9c"
    }
    cookies = {
        "abRequestId": "06b73935-c0f6-53d1-8c4b-f99e90358eed",
        "xsecappid": "xhs-pc-web",
        "a1": "199ce8e93b2kr36a9orz18xi4x3w8hf0ccow6h9kz50000398176",
        "webId": "9642ef0f0e0c4920f51ee088cc7657c7",
        "gid": "yjjSdYdfSdSWyjjSdYdjqSxjDJTFqK0jlFuylTuYC34CqE28EYxi8K888qjYyWK8448fJSSK",
        "ets": "1775564252728",
        "webBuild": "6.4.1",
        "id_token": "VjEAAABVa4IFmiGt1nmJvG2gBMbcBEvhetKwEAHi7AYQjSVi1Rz9Zn72H0ycij3YvlVgF5gO2mv/eHoOWWJhb1owDG5pygQPbJWfZfCKNi19gkz0hjRl6faHQ3zotZxZL3rxMdTq",
        "websectiga": "10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467",
        "sec_poison_id": "54857159-1cf0-470a-b30c-478cd4d93ce9",
        "acw_tc": "0ad6fbdf17756289661933167e6c52cc9f6b4d9d4c8d66491da073b380747a",
        "web_session": web_session,
        "unread": "{%22ub%22:%2269d29526000000001d01df6b%22%2C%22ue%22:%2269d3b6490000000023004a71%22%2C%22uc%22:40}",
        "loadts": "1775629058366"
    }
    url = "https://edith.xiaohongshu.com/api/sns/web/v2/comment/page"
    params = {
        "note_id": "6831c633000000002301241b",
        "cursor": "",
        "top_comment_id": "",
        "image_formats": "jpg,webp,avif",
        "xsec_token": "ABuDSsTVLWx3T1h7D74q0zOC76MrpKJCR8p5d9pL27m_E="
    }
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    return response

print(msg('0400698f876588565e4bf94be33b4b292e0dce').text)
