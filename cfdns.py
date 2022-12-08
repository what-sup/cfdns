import random
import time
import json
import urllib3
import traceback
import jsonpath
import requests
urllib3.disable_warnings()

# KEY可以从 https://shop.hostmonit.com 获取，或者使用以下免费授权
KEY = "o1zrmHAF"
TYPE = 'v4' #暂时只支持A记录

DOMAINS = {
	"你的cloudflare api": {
		"你要修改的域名ID1": {
			"你要修改的域名解析记录ID": {
				"你的邮箱": "CM" # 网络类型： 移动-CM; 联通-CU; 电信-CT
			},
			"你要修改的域名解析记录ID": {
				"你的邮箱": "CU"
			},
			"你要修改的域名解析记录ID": {
				"你的邮箱": "CT"
			}
		},
		"你要修改的域名ID2": {
			#格式如上
		}
	}
}

def get_ip():
    try:
        http = urllib3.PoolManager()
        headers = headers = {'Content-Type': 'application/json'}
        data = {"key": KEY, "type": TYPE}
        data = json.dumps(data).encode()
        response = http.request('POST','https://api.hostmonit.com/get_optimization_ip',body=data, headers=headers)
        return json.loads(response.data.decode('utf-8'))
    except Exception as e:
        print(e)
        return None

def get_by_time(cfips, path):
	ret = ''
	ippath = '$.info.' + path + "..ip"
	timepath = '$.info.' + path + "..time"
	ips = jsonpath.jsonpath(cfips, ippath)
	times = jsonpath.jsonpath(cfips, timepath)
	tmptime = str(times[0])
	for i in range(len(ips)):
		if tmptime > times[i]:
			tmptime = times[i]
			ret = ips[i]
	return ret


def put_cf(api, domain, dns, mail, net, ips):
	ip = get_by_time(ips, net)
	url = "https://api.cloudflare.com/client/v4/zones/" + domain + "/dns_records/" + dns
	head = {
		"Content-Type": "application/json",
		"X-Auth-Email": mail,
		"X-Auth-Key": api
	}
	data = '{"content": "'+ ip + '"}'
	print(ip)
	print(url)
	print(requests.patch(url, headers = head, data = data).content)


def main():
	if len(DOMAINS) > 0:
		try:
			cfips = get_ip()
			for api, domains in DOMAINS.items():
				for domain, dnss in domains.items():
					for dns, mails in dnss.items():
						for mail, net in mails.items():
							put_cf(api, domain, dns, mail, net, cfips)
		except Exception as e:
			print(e)

if __name__ == '__main__':
	main()