# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""
import json,urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from common.mymako import render_mako_context
from zabbix_api import ZabbixAPI

def helloword(request):
    zapi = ZabbixAPI(server="http://192.168.0.194/zabbix/api_jsonrpc.php")
    zapi.login("Admin", "zabbix")  # 鉴权
    abc = zapi.trigger.get({"expandExpression":"extend","triggerids":range(0,100 )})
    a = abc
    zabbix_url = "http://192.168.0.194/zabbix/api_jsonrpc.php"
    zabbix_header = {"Content-Type": "application/json"}
    zabbix_user = "Admin"
    zabbix_pass = "zabbix"
    auth_code = ""
    result_value = []
    itemid = ''
    memorysize = ''
    # 用户认证信息的部分，最终的目的是得到一个SESSIONID
    # 这里是生成一个json格式的数据，用户名和密码
    auth_data = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params":
                {
                    "user": zabbix_user,
                    "password": zabbix_pass
                },
            "id": 0
        })

    # 创建 request 对象  构造请求数据
    request = urllib2.Request(zabbix_url, auth_data)

    for key in zabbix_header:
        request.add_header(key, zabbix_header[key])
    # 认证和获取sessionid
    try:
        result = urllib2.urlopen(request)
    # 对于出错的处理
    except HTTPError, e:
        print 'The server couldn\'t fulfill the request, Error code: ', e.code
    except URLError, e:
        print 'We failed to reach a server.Reason: ', e.reason
    else:
        response = json.loads(result.read())
        print response
        result.close()

    #判断SESSIONID是否在返回的数据中
    if 'result' in response:
        auth_code = response['result']
    else:
        print  response['error']['data']

    # request json
    # 用得到的SESSIONID去通过验证，获取主机的信息（用http.get方法）
    if len(auth_code) <> 0:
        host_list = []
        get_host_data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "output": "extend",
                    "selectInterfaces": [
                        "ip"
                    ]
                },
                "auth": auth_code,
                "id": 1,
            })

        # 创建 request 对象
        request = urllib2.Request(zabbix_url, get_host_data)
        for key in zabbix_header:
            request.add_header(key, zabbix_header[key])

        # 获取 host 列表
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
        else:
            response = json.loads(result.read())
            result.close()
            # 将所有的主机信息显示出来
            for r in response['result']:
                print ('aaaaa',r['hostid'],r['host'])
                dics = {}
                dics['ip'] = r['interfaces'][0]['ip']
                dics['hostid'] = r['hostid']
                dics['memory_available'] = ''
                host_list.append(dics)

            # 显示主机的个数
            print "Number Of Hosts: ", len(host_list)
        # 获取监控对象
    for item in host_list:
        get_item_obj = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": ["extend"],
                "hostids":item['hostid'],
                "search": {
                    "key_": "vm.memory.size[available]"
                },
                "sortfield": "name"
            },
            "auth": auth_code,
            "id": 1,
        })
        request = urllib2.Request(zabbix_url, get_item_obj)
        for key in zabbix_header:
            request.add_header(key, zabbix_header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
        else:
            item_obj = json.loads(result.read())
            if item_obj['result']:
                itemid = item_obj['result'][0]['itemid']
            result.close()

        get_history_obj = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "history.get",
                "params": {
                    "output": "extend",
                    "history": 3,
                    "itemids": itemid,
                    "limit": 10
                },
                "auth": auth_code,
                "id": 1,
            })
        request = urllib2.Request(zabbix_url, get_history_obj)
        for key in zabbix_header:
            request.add_header(key, zabbix_header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server could not fulfill the request.'
                print 'Error code: ', e.code
        else:
            history_obj = json.loads(result.read())
            result.close()
            for item in history_obj['result']:
                result_value.append(item)
                item['memory_available'] = int(item['value'])//1024//1024//1024
                host_list[i]['memory_available'] = int(item['value'])//1024//1024//1024
    return render_mako_context(request, '/home_application/test1.html',{"host_list":host_list})






