import random
import time
import json
import urllib3
import traceback
import jsonpath
import requests
import yaml
urllib3.disable_warnings()

# KEY可以从 https://shop.hostmonit.com 获取，或者使用以下免费授权
KEY = "o1zrmHAF"
TYPE = 'v4' #暂时只支持A记录

with open("config.yaml", 'r',encoding='utf-8') as stream:
    try:
        config = yaml.load(stream.read(), Loader=yaml.FullLoader)
        DOMAINS = config['CONFIG']
        MODE = config['MODE']
        print(DOMAINS)
    except Exception as e:
        print(e)

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
	ippath = '$.info.' + path + "..ip"
	timepath = '$.info.' + path + "..time"
	losspath = '$.info.' + path + "..loss"
	ips = jsonpath.jsonpath(cfips, ippath)
	times = jsonpath.jsonpath(cfips, timepath)
	losses = jsonpath.jsonpath(cfips, losspath)
	tmptime = str(times[0])
	ret = ips[0]
	for i in range(len(ips)):
		if tmptime > times[i] and losses[i] == 0:
			tmptime = times[i]
			ret = ips[i]
	return ret

def get_by_speed(cfips, path):
	ippath = '$.info.' + path + "..ip"
	speedpath = '$.info.' + path + "..speed"
	losspath = '$.info.' + path + "..loss"
	ips = jsonpath.jsonpath(cfips, ippath)
	speeds = jsonpath.jsonpath(cfips, speedpath)
	losses = jsonpath.jsonpath(cfips, losspath)
	tmpspeed = int(speeds[0])
	ret = ips[0]
	for i in range(len(ips)):
		if tmpspeed < speeds[i] and losses[i] == 0:
			tmpspeed = speeds[i]
			ret = ips[i]

	return ret

def get_by_latency(cfips, path):
	ippath = '$.info.' + path + "..ip"
	latencypath = '$.info.' + path + "..latency"
	losspath = '$.info.' + path + "..loss"
	ips = jsonpath.jsonpath(cfips, ippath)
	latencys = jsonpath.jsonpath(cfips, latencypath)
	losses = jsonpath.jsonpath(cfips, losspath)
	tmplatency = int(latencys[0])
	ret = ips[0]
	for i in range(len(ips)):
		if tmplatency > latencys[i] and losses[i] == 0:
			tmplatency = latencys[i]
			ret = ips[i]
	return ret



def put_cf(mail, api, domain, dns, net, region, cfips):
	ips = get_ip_by_region(ips, region)
	if MODE == 1:
		ip = get_by_time(ips, net)
	elif MODE == 2:
		ip = get_by_speed(ips, net)
	elif MODE == 3:
		ip = get_by_latency(ips, net)
	url = "https://api.cloudflare.com/client/v4/zones/" + domain + "/dns_records/" + dns
	head = {
		"Content-Type": "application/json",
		"X-Auth-Email": mail,
		"X-Auth-Key": api
	}
	data = '{"content": "'+ ip + '"}'
	print(ip)
	print(net)
	print(url)
	print(requests.patch(url, headers = head, data = data).content)
	

def main():
	if len(DOMAINS) > 0:
		try:
			cfips = get_ip()
			#print(cfips)
			for mail, apis in DOMAINS.items():
				for api, domains in apis.items():
					for domain, dnss in domains.items():
						for dns, nets in dnss.items():
							for net, region in nets.items():
								put_cf(mail, api, domain, dns, net, region, cfips)
		except Exception as e:
			print(e)

if __name__ == '__main__':
	main()