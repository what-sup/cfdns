import random
import time
import json
import urllib3
import traceback
import jsonpath
import requests
import yaml
from log import Logger

# KEY可以从 https://shop.hostmonit.com 获取，或者使用以下免费授权
KEY = "o1zrmHAF"
TYPE = 'v4' #暂时只支持A记录
FORCE = 0

log_debug = Logger('cfdns.log', level='debug')
urllib3.disable_warnings()

with open("config.yaml", 'r',encoding='utf-8') as stream:
	config = yaml.load(stream.read(), Loader=yaml.FullLoader)
	DOMAINS = config['CONFIG']
	MODE = config['MODE']

'''
with open("ips.log", 'r',encoding='utf-8') as stream:
	pass
'''

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


def get_by_time(cfips):
	ippath = "$..ip"
	timepath = "$..time"
	losspath = "$..loss"
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

def get_by_speed(cfips):
	ippath = "$..ip"
	speedpath = "$..speed"
	losspath = "$..loss"
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

def get_by_latency(cfips):
	ippath = "$..ip"
	latencypath = "$..latency"
	losspath = "$..loss"
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

def get_ip_by_region(cfips, net, region):
	ippath = '$.info.' + net + "..ip"
	regionpath = '$.info.' + net + "..colo"
	tmppath = '$.info.' + net + ".*"
	ips = jsonpath.jsonpath(cfips, ippath)
	regions = jsonpath.jsonpath(cfips, regionpath)
	tmpips = jsonpath.jsonpath(cfips, tmppath)
	ret = []
	cnt = 0
	for i in range(len(ips)):
		if regions[i] == region:
			ret.append(tmpips[i])
			cnt += 1
	if len(ret) == 0 and FORCE == 0:
		ret = [-1]
	return ret

def put_cf(mail, api, domain, dns, net, region, cfips):
	ips = get_ip_by_region(cfips, net, region)
	log_debug.logger.info(ips)
	if(ips == [-1]):
		log_debug.logger.error("No ip found in " + region)
		return
	if ips == []:
		ips = cfips
#	ips = cfips
	if MODE == 1:
		ip = get_by_time(ips)
	elif MODE == 2:
		ip = get_by_speed(ips)
	elif MODE == 3:
		ip = get_by_latency(ips)
	url = "https://api.cloudflare.com/client/v4/zones/" + domain + "/dns_records/" + dns
	head = {
		"Content-Type": "application/json",
		"X-Auth-Email": mail,
		"X-Auth-Key": api
	}
	data = '{"content": "'+ ip + '"}'
	log_debug.logger.info(ip)
	log_debug.logger.info(net)
	log_debug.logger.info(url)
	log_debug.logger.info(requests.patch(url, headers = head, data = data).content)
	

def main():	
	    	
	cfips = get_ip()
	log_debug.logger.info(cfips)
	mail = DOMAINS['your_email']
	api = DOMAINS['api']
	DOMAINS.pop('your_email')
	DOMAINS.pop('api')
	i = iter(DOMAINS)

	for each_domain in i:
		domain = each_domain
		dnses = DOMAINS[domain]
		for dns in dnses:
			nets = dnses[dns]
			for net in nets:
				regions = nets[net]
				log_debug.logger.info(regions)
				put_cf(mail, api, domain, dns, net, regions, cfips)

if __name__ == '__main__':
	main()