# cfdns
## 原理
使用 [这个网站](https://stock.hostmonit.com/CloudFlareYes) 提供的优质dns（有能力请支持下这个，可以从[这里](https://shop.hostmonit.com)购买KEY）

并调用cloudflare api更新dns记录

因为 [这个project](https://github.com/ddgth/cf2dns) 没支持cloudflare, 这个可以暂时作为替代品

配合crontab可以定时更新优选ip

## 如何获取cloudflare api, 域名ID等信息

[这里](https://github.com/XIU2/CloudflareSpeedTest/issues/40) 有详细教程，这里不详细展开

## credit
[cf2dns](https://github.com/ddgth/cf2dns)

[XIU2/CloudflareSpeedTest](https://github.com/XIU2/CloudflareSpeedTest)

[CloudFlare优质IP](https://stock.hostmonit.com/CloudFlareYes)

## 快速使用
使用pip install -r requirements.txt快速安装依赖库
修改config.yaml
- MODE  1-取最新ip; 2-取速度最快ip; 3-取延迟最低ip
