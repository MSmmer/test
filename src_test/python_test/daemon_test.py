#!/usr/bin/env python
# -*- encoding:utf-8 -*-
'''
Created on 2014年12月18日
 
@author: liujichao
'''
import datetime
import json
import re
import sys
import time
from PIL import Image
import PyV8
import requests
 
import tools.email_helper as emailHelper
 
 
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable
reqSingle = requests.Session()
attCheCi=["G655","G6741","G67","G491"] #关注的车次
dateList=["2015-02-18"] #关注的日期
username="12306登录用户名"
password="登录密码"
#这个是需要手动提交订单后f12自己找的，挨个post请求去找，参数名为：oldPassengerStr 格式如下
oldPassengerStr="姓名,1,130434199802036011,1_姓名2,1,130434199204238069,1_"
#这个是需要手动提交订单后f12自己找的，挨个post请求去找，参数名为：passengerTicketStr 格式如下
passengerTicketStr="O,0,1,姓名,1,130434199802036011,13683456789,N_O,0,1,姓名2,1,130434199204238069,13683456789,N"
header={
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            "Connection":"keep-alive",
            "Host":"kyfw.12306.cn",
            "Referer":"https://kyfw.12306.cn/otn/safeguard/init",
            "User-Agent":"Mozilla/5.0 (Windows NT 5.1; rv:34.0) Gecko/20100101 Firefox/34.0"
            }
##定火车票 
def orderTicket(fromStation,toStation,trainDate,secretStr):
    header["Referer"]="https://kyfw.12306.cn/otn/leftTicket/init"
    orderInitReq= reqSingle.get("https://kyfw.12306.cn/otn/leftTicket/init",headers=header)
    header["Referer"]="https://kyfw.12306.cn/otn/leftTicket/init"
    aryKV=extractKey(orderInitReq.content,header)
    print aryKV
    #初始化订票
    header["Referer"]="https://kyfw.12306.cn/otn/leftTicket/init"
    orderInitReq= reqSingle.post("https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest",data={
                                                                                   aryKV[0]:aryKV[1],
                                                                                   "train_date":trainDate,
                                                                                   "myversion":"undefined",
                                                                                   "purpose_codes":"ADULT",
                                                                                   "query_from_station_name":fromStation,
                                                                                   "query_to_station_name":toStation,
                                                                                   "secretStr":secretStr,
                                                                                   "tour_flag":"dc",
                                                                                   "back_train_date":time.strftime('%Y-%m-%d',time.localtime(time.time())),
                                                                                   "undefined":""
                                                                                   },headers=header)
    print orderInitReq.content
    orderInitJson=orderInitReq.json()
    if orderInitJson.get("status")==False or  orderInitJson.get("httpstatus")!=200:
        raise Exception("订票出现错误")
    initDcReq= reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/initDc", data={"_json_att":""},headers=header)
    header["Referer"]="https://kyfw.12306.cn/otn/confirmPassenger/initDc"
    aryKV=extractKey(initDcReq.content,header)
    match =re.search("var globalRepeatSubmitToken = '(.*?)';", initDcReq.content)
    ticketToken=match.group(1)
    lianxirenReq=reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs", data={"REPEAT_SUBMIT_TOKEN":ticketToken,"_json_att":""},headers=header)
    lianxirenJson=lianxirenReq.json()
    #验证码
     #开始做验证码
    while True:
        r=reqSingle.get("https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&",verify=False,timeout=5,headers=header)
        with open("orderRand.jpg","wb") as rimg:
            rimg.write(r.content)
            pass
        img=Image.open("orderRand.jpg")
        img.show()
        randCode=raw_input("请输入登录验证码:")
        #验证验证码
        randReq= reqSingle.post("https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn",data={
                                                                                                 "REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                                 "_json_att":"",
                                                                                                 "rand":"randp",
                                                                                                 "randCode":randCode},headers=header)
        randRes=randReq.json()
        if randRes.get("status") and randRes.get("httpstatus")==200 and randRes.get("data").get("result")=="1":
            break;
        pass
    print "验证码输入正确！"
    #检查票
    checkOrderInfoReq=reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo", data={
                                                                                      aryKV[0]:aryKV[1],
                                                                                      "REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                      "_json_att":"",
                                                                                      "bed_level_order_num":"000000000000000000000000000000",
                                                                                      "cancel_flag":2,
                                                                                      "oldPassengerStr":oldPassengerStr,
                                                                                      "passengerTicketStr":passengerTicketStr,
                                                                                      "randCode":randCode,
                                                                                      "tour_flag":"dc"
                                                                                      })
    checkOrderInfoJson=checkOrderInfoReq.json()
    if checkOrderInfoJson.get("status")==False or checkOrderInfoJson.get("httpstatus")!=200:
        raise Exception("检查票出现错误")
        pass
    fromStationTelecode=re.search("'from_station_telecode':'(.*?)'", initDcReq.content).group(1)
    leftTicket=re.search("'ypInfoDetail':'(.*?)'", initDcReq.content).group(1)
    purpose_codes=re.search("'purpose_codes':'(.*?)'", initDcReq.content).group(1)
    station_train_code=re.search("'station_train_code':'(.*?)'", initDcReq.content).group(1)
    to_station_telecode=re.search("'to_station_telecode':'(.*?)'", initDcReq.content).group(1)
    train_no=re.search("'train_no':'(.*?)'", initDcReq.content).group(1)
    queueCountReq=reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount",data={
                                                                                    "REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                    "_json_att":"",
                                                                                    "fromStationTelecode":fromStationTelecode,
                                                                                    "leftTicket":leftTicket,
                                                                                    "purpose_codes":purpose_codes,
                                                                                    "seatType":0,
                                                                                    "stationTrainCode":station_train_code,
                                                                                    "toStationTelecode":to_station_telecode,
                                                                                    "train_date":datetime.datetime.fromtimestamp(time.mktime(time.strptime(trainDate,'%Y-%m-%d'))).strftime('%a %b %d %Y %H:%M:%S GMT+0800'),
                                                                                    "train_no":train_no
                                                                                    },headers=header)
    queueCountJson=queueCountReq.json()
    print queueCountReq.content
    if queueCountJson.get("status")==False or queueCountJson.get("httpstatus")!=200:
        raise Exception("获取队列错误")
     
    #确认队列
    key_check_isChange=re.search("'key_check_isChange':'(.*?)'", initDcReq.content).group(1)
    train_location=re.search("'train_location':'(.*?)'", initDcReq.content).group(1)
     
    singleForQueueReq=reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue",data={
                                                                                                              "REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                                               "_json_att":"",
                                                                                                               "dwAll":"N",
                                                                                                               "key_check_isChange":key_check_isChange,
                                                                                                               "leftTicketStr":leftTicket,
                                                                                                               "oldPassengerStr":oldPassengerStr,
                                                                                                               "passengerTicketStr":passengerTicketStr,
                                                                                                               "purpose_codes":purpose_codes,
                                                                                                               "randCode":randCode,
                                                                                                               "train_location":train_location
                                                                                                              },headers=header)
      
    singleForQueueJson=singleForQueueReq.json()
    print singleForQueueReq.content
    if singleForQueueJson.get("status")==False or singleForQueueJson.get("httpstatus")!=200:
        raise Exception("confirmSingleForQueue异常")
    if singleForQueueJson.get("data") is None or singleForQueueJson.get("data").get("submitStatus")==False:
        raise Exception("confirmSingleForQueue异常")
    #等待orderid
    while True:
        orderWaitReq= reqSingle.get("https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime",data={"REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                            "_json_att":"",
                                                                                            "random":time.time(),
                                                                                            "tourFlag":"dc"
                                                                                            },headers=header)
        print orderWaitReq.content
        orderWaitJson=orderWaitReq.json()
        if orderWaitJson.get("status") and orderWaitJson.get("httpstatus")==200:
            if orderWaitJson.get("data") is not None and orderWaitJson.get("data").get("orderId") is not None:
                orderId=orderWaitJson.get("data").get("orderId")
                break
            pass
        pass
    #进入队列
    dcQueueReq=reqSingle.post("https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue",data={
                                                                                            "REPEAT_SUBMIT_TOKEN":ticketToken,
                                                                                            "_json_att":"",
                                                                                            "orderSequence_no":orderId
                                                                                            }
                   ,headers=header)
    dcQueueJson=dcQueueReq.json()
    if dcQueueJson.get("status") and dcQueueJson.get("httpstatus")==200 and dcQueueJson.get("data") is not None and dcQueueJson.get("data").get("submitStatus"):
        print "订票成功"
        pass
    else:
        print dcQueueJson.content
        print "订票失败"
        pass
      
     
    #https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue
    pass
#检查是否登录 
def checkIsLogin():
    checkReq= reqSingle.post("https://kyfw.12306.cn/otn/login/checkUser", data={"_json_att":""},headers=header)
    print u"检查是否登录"+checkReq.content
    checkReqJson=checkReq.json()
    if checkReqJson.get("status") and checkReqJson.get("httpstatus")==200:
        if checkReqJson.get("data") is not None and checkReqJson.get("data").get("flag"):
            return True
        pass
    return False
    pass
#提取js加密内容后的key和value
def extractKey(htmlContent,headerxx):
    loginMatch=re.search(r'<script src="(/otn/dynamicJs/.*?)" type="text/javascript" xml:space="preserve"></script>', htmlContent)
    jsUrl="https://kyfw.12306.cn"+ loginMatch.group(1)
    jsReq=reqSingle.get(jsUrl,verify=False,timeout=15,headers=headerxx)
    jsContent= jsReq.content
    jsMatch=re.search("(function bin216.*?)function aj", jsContent)
    jsEncode= jsMatch.group(1)#获取加密的js内容
    keyMatch=re.search("var key='(.*?)'",jsContent)
    loginKey= keyMatch.group(1)#获取登录的key
    ctx=PyV8.JSContext()
    ctx.enter()
    ctx.eval(jsEncode)
    loginValue=ctx.locals.encode32(ctx.locals.bin216(ctx.locals.Base32.encrypt( "1111",loginKey)))
    return [loginKey,loginValue]
    pass
#登录操作
def login():
    header["Referer"]="https://kyfw.12306.cn/otn/login/init"
    r=reqSingle.get("https://kyfw.12306.cn/otn/login/init",verify=False,timeout=15,headers=header)
    loginContent=r.content
    aryKV=extractKey(loginContent,header)
    #开始做验证码
    while True:
        r=reqSingle.get("https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&",verify=False,timeout=5,headers=header)
        with open("loginRand.jpg","wb") as rimg:
            rimg.write(r.content)
            pass
        img=Image.open("loginRand.jpg")
        img.show()
        randCode=raw_input("请输入登录验证码:")
        #验证验证码
        randReq= reqSingle.post("https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn",data={"rand":"sjrand","randCode":randCode},headers=header)
        randRes=randReq.json()
        if randRes.get("status") and randRes.get("httpstatus")==200 and randRes.get("data").get("result")=="1":
            break;
        pass
    print "验证码输入正确！"
     
    #开始登陆
    loginRes=reqSingle.post("https://kyfw.12306.cn/otn/login/loginAysnSuggest",data={
                                                                           aryKV[0]:aryKV[1],
                                                                           "loginUserDTO.user_name":username,
                                                                           "userDTO.password":password,
                                                                           "randCode":randCode,
                                                                           "myversion":"undefined",
                                                                           "randCode_validate":""
                                                                           },headers=header)
    print repr(r.request)
    print loginRes.content
    loginResJson=loginRes.json()
    if loginResJson.get("status") and loginResJson.get("httpstatus")==200:
        if loginResJson.get("data") is not None and loginResJson.get("data").get("loginCheck")=="Y":
            print "登录成功"
        else:
            raise Exception(loginRes.content)
    else:
        login()
    pass
def checkTicket(dtStr):
    print dt
    while True:
        try:
            r= requests.get("https://kyfw.12306.cn/otn/leftTicket/queryT?leftTicketDTO.train_date="+dtStr+"&leftTicketDTO.from_station=BXP&leftTicketDTO.to_station=HDP&purpose_codes=ADULT",verify=False,timeout=5,headers=header)
            break
        except Exception:
            pass
        pass
    #print r.contentfd
    print r.content
    try:
        queryDataJson= json.loads(r.content)
    except Exception:
        return
    if queryDataJson["httpstatus"]==200 and queryDataJson["status"] :
        #print queryDataJson["data"]
        for checi in queryDataJson["data"]:
            tmpData=checi["queryLeftNewDTO"]
            trainCode=tmpData.get("station_train_code")
            #yzNum=tmpData.get("yz_num")
            yzNum=tmpData.get("ze_num")
             
            if trainCode in attCheCi:
                 
                if yzNum!="--" and yzNum!="无" and (yzNum=="有" or int(yzNum)>=2):
                    #发邮件
                     
                    fromStation=tmpData.get("start_station_name")
                    toStation=tmpData.get("end_station_name")
                    secretStr=checi.get("secretStr")
                    orderTicket(fromStation, toStation, dtStr, secretStr)
#                     body=dtStr+"-"+trainCode+"-"+yzNum+u"个硬座"
#                     print body
#                     mailer=emailHelper.email_helper("smtp.qq.com", "fd", "fss", "qq.com","plain")
#                     mailer.send("630419595@qq.com", u"有火车票了",body)
#                     raise Exception("有票了")
                    pass
                print trainCode+yzNum
            pass
        pass
    pass
if __name__ == '__main__':
#     login()
#     if checkIsLogin():
#         print "登录成功"
#     
#     orderTicket("北京西","邯郸东","2015-01-14","MjAxNS0wMS0xNCMwMCNHNjczMSMwMjoxNSMwNzowNSMyNDAwMEc2NzMxMDUjQlhQI0hQUCMwOToyMCPljJfkuqzopb8j6YKv6YO45LicIzAxIzA2I08wMDAwMDA4MThNMDAwMDAwMTEwOTAwMDAwMDAyNiNQMiMxNDE5MDg2OTU2MTA0IzI5NEI0QkY0QTU2ODE2RDU1MzE5RkRCRkVEQzQ3Mzk2MUEyRUEwOEM0MUVCMjZGMDc3RUUyNzc0")
#     exit()
    login()
    if checkIsLogin():
        print "登录成功"
    while True:
        checkCount=0
        for dt in dateList:
            checkTicket(dt)
            time.sleep(2)
            checkCount+=1
            if checkCount%10==0:
                if checkIsLogin():
                    print "成功状态"
                else:
                    print "被踢了"
            pass
    pass
