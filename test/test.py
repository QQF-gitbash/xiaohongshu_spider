import requests
import json


headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "content-type": "application/json;charset=UTF-8",
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
    # "x-b3-traceid": "ccd1b70fb18f890d",
    # "x-rap-param": "ByQBBQAAAAEAAAAUAAAApKRBP40AACcRAAAAGAAAAAAAAAAAZG1pN2FVgEhS3JONOFUp+weKTTXMAAAAEPiY/dVLofpShmbSV2P6K2e5kE8gfVrzpv8BIx7nGJQdiHhRA8OjFEunvn9QpLDCIdzsGnr8hD+PEr8YyXnHPKE7v0CjJB8+CFv5m2SL49isGQeBd1mv8h9UqbrgZqWJQzTYyE+W25b4mRARN9Z6Flio2iFv2fuO3hgDW+t9iD5gyxhtwnBU+obPUqjBc8E1kEqi6FAmThQbtyLKs5kfhjMAAACb",
    "x-s": "XYS_2UQhPsHCH0c1PUhAHjIj2erjwjQhyoPTqBPT49pjHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQTJdPIPAZlg94aGLTlLgYxz7SQPpp8aDEbqemk8rpx+omHp9+awepnJURx2bSi8rDUyfEf+7iF8bYLPaRILBlNPfMrLgSIpnbsweH3GDRAcdbOJDEEnaVEzSZELS+h/F8+J9RO/MpG4DR6/dDFadS3PDbearlT/MYPJp8mPrkHaMY/+FTpznbTPB8+c9EIqMQCLDkcpnbLP9II/LT/Jfznnfl0yLLIaSQQyAmOarEaLSz+GdYzPoDF//Z9+M4I4gG74DYccnVItUHVHdWFH0ijJ9Qx8n+FHdF=",
    "x-s-common": "2UQAPsHC+aIjqArjwjHjNsQhPsHCH0rjNsQhPaHCH0c1PUhAHjIj2eHjwjQgynEDJ74AHjIj2ePjwjQhyoPTqBPT49pjHjIj2ecjwjH9N0c1PaHVHdWMH0ijP/DEG9Lh8/DAG0Q3q0P9G/S6qdilwoYk+oWA4AYi80m0G9R7+fWEy7iMPeZIPePEwer7+jHVHdW9H0ijHjIj2eqjwjHjNsQhwsHCHDDAwoQH8B4AyfRI8FS98g+Dpd4daLP3JFSb/BMsn0pSPM87nrldzSzQ2bPAGdb7zgQB8nph8emSy9E0cgk+zSS1qgzianYt8p+1/LzN4gzaa/+NqMS6qS4HLozoqfQnPbZEp98QyaRSp9P98pSl4oSzcgmca/P78nTTL08z/sVManD9q9z1J9p/8db8aob7JeQl4epsPrz6agW3Lr4ryaRApdz3agYDq7YM47HFqgzkanYMGLSbP9LA/bGIa/+nprSe+9LI4gzVPDbrJg+P4fprLFTALMm7+LSb4d+kpdzt/7b7wrQM498cqBzSpr8g/FSh+bzQygL9nSm7qSmM4epQ4flY/BQdqA+l4oYQ2BpAPp87arS34nMQyF8E8nkdqMD6pMzd8/4SL7bF8aRr+7+rG7mkqBpD8pSUzozQcA8Szb87PDSb/d+/qgzVJfl/4LExpdzQ4fRSy7bFP9+y+7+nJAzdaLp/2LSiz/QzwgbMagYiJdbCwB4QyFSfJ7b7yFSenS4oJA+A8BlO8p8c4A+Q4DbSPB8d8nz/zBEQye4A2BrF/g4M4epQzLTApBRm8nz+a7PApd4C8n8d8Lzl4opQ2BSTGSpDq9zM4rpAq94SngbFJFS9yLRQc7rlq7pFqrQn4FRd+AYS49+N8pP7+npLpd4CanSO8/ZEcnLAp9laanYD8p+V+dP9JMzVanW9q9zl4AmQznQnwopFPd4c4e+Q2BpApDDROaHVHdWEH0ilweqU+AW9PAr7NsQhP/Zjw0ZVHdWlPaHCHfE6qfMYJsHVHdWlPjHCH0r7+AL9P0LhwePhP0ZvP/q7+ecU+0ch+/PA+jQR",
    # "x-t": "1775625957776",
    # "x-xray-traceid": "ceb5c6f8bd5a69863d1605b4b1373e4d",
    # "xy-direction": "24"
}
cookies = {
    "abRequestId": "06b73935-c0f6-53d1-8c4b-f99e90358eed",
    "xsecappid": "xhs-pc-web",
    "a1": "199ce8e93b2kr36a9orz18xi4x3w8hf0ccow6h9kz50000398176",
    "webId": "9642ef0f0e0c4920f51ee088cc7657c7",
    "gid": "yjjSdYdfSdSWyjjSdYdjqSxjDJTFqK0jlFuylTuYC34CqE28EYxi8K888qjYyWK8448fJSSK",
    "ets": "1775564252728",
    "webBuild": "6.4.1",
    "acw_tc": "0a5088c617756258286782250e5ab5dceb75e7f839ffdddef83301b989596c",
    "websectiga": "29098a4cf41f76ee3f8db19051aaa60c0fc7c5e305572fec762da32d457d76ae",
    "sec_poison_id": "5bfc4df9-0e86-4f4c-a838-4ba1bdb24b79",
    "loadts": "1775625882979",
    "unread": "{%22ub%22:%2269d3762f000000001a029bc3%22%2C%22ue%22:%2269d2cbb40000000021005934%22%2C%22uc%22:30}",
    "web_session": "030037aee55576aab0b24e47ae2e4a726343c4",
    "id_token": "VjEAAABVa4IFmiGt1nmJvG2gBMbcBEvhetKwEAHi7AYQjSVi1Rz9Zn72H0ycij3YvlVgF5gO2mv/eHoOWWJhb1owDG5pygQPbJWfZfCKNi19gkz0hjRl6faHQ3zotZxZL3rxMdTq"
}
url = "https://edith.xiaohongshu.com/api/sns/web/v1/homefeed"
data = {
    "cursor_score": "",
    "num": 35,
    "refresh_type": 1,
    "note_index": 35,
    "unread_begin_note_id": "",
    "unread_end_note_id": "",
    "unread_note_count": 0,
    "category": "homefeed_recommend",
    "search_key": "",
    "need_num": 10,
    "image_formats": [
        "jpg",
        "webp",
        "avif"
    ],
    "need_filter_image": False
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, cookies=cookies, data=data)

print(response.text)
print(response)