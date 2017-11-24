# -*- coding: utf-8 -*-
from LineAlpha import LineClient
from LineAlpha.LineApi import LineTracer
from LineAlpha.LineThrift.ttypes import Message
from LineAlpha.LineThrift.TalkService import Client
import time, datetime, random ,sys, re, string, os, json

reload(sys)
sys.setdefaultencoding('utf-8')

client = LineClient()
client._qrLogin("line://au/q/")

profile, setting, tracer = client.getProfile(), client.getSettings(), LineTracer(client)
offbot, messageReq, wordsArray, waitingAnswer = [], {}, {}, {}

print client._loginresult()

wait = {
    'autoAdd':True,
	'message':"Hello World!",
    'readPoint':{},
    'readMember':{},
    'setTime':{},
    'ROM':{}
   }

setTime = {}
setTime = wait["setTime"]

def sendMessage(to, text, contentMetadata={}, contentType=0):
    mes = Message()
    mes.to, mes.from_ = to, profile.mid
    mes.text = text

    mes.contentType, mes.contentMetadata = contentType, contentMetadata
    if to not in messageReq:
        messageReq[to] = -1
    messageReq[to] += 1
    client._client.sendMessage(messageReq[to], mes)

def NOTIFIED_ADD_CONTACT(op):
    try:
        sendMessage(op.param1, client.getContact(op.param1).displayName + "感謝您將本帳設為好友(*´･ω･*)\n\n萬一您覺得提醒的次數有點多，您可以在本畫面的聊天室設定選單中，將「提醒」的功能關掉喔！(ok)")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_ADD_CONTACT\n\n")
        return

tracer.addOpInterrupt(5,NOTIFIED_ADD_CONTACT)

def NOTIFIED_KICKOUT_FROM_GROUP(op):
    try:
        sendMessage(op.param1, "警告：" + client.getContact(op.param3).displayName + "被踢出")
    except Exception as e:
        print e
        print ("\n\nNOTIFIED_KICKOUT_FROM_GROUP\n\n")
        return

tracer.addOpInterrupt(19,NOTIFIED_KICKOUT_FROM_GROUP)

def NOTIFIED_READ_MESSAGE(op):
    #print op
    try:
        if op.param1 in wait['readPoint']:
            Name = client.getContact(op.param2).displayName
            if Name in wait['readMember'][op.param1]:
                pass
            else:
                wait['readMember'][op.param1] += "\n・" + Name
                wait['ROM'][op.param1][op.param2] = "・" + Name
        else:
            pass
    except:
        pass

tracer.addOpInterrupt(55, NOTIFIED_READ_MESSAGE)

def RECEIVE_MESSAGE(op):
    msg = op.message
    try:
        if msg.contentType == 0:
            try:
                if msg.to in wait['readPoint']:
                    if msg.from_ in wait["ROM"][msg.to]:
                        del wait["ROM"][msg.to][msg.from_]
                else:
                    pass
            except:
                pass
        else:
            pass
    except KeyboardInterrupt:
	       sys.exit(0)
    except Exception as error:
        print error
        print ("\n\nRECEIVE_MESSAGE\n\n")
        return

tracer.addOpInterrupt(26, RECEIVE_MESSAGE)

def SEND_MESSAGE(op):
    msg = op.message
    try:
        if msg.toType == 0:
            if msg.contentType == 0:
                if msg.text == "mid":
                    sendMessage(msg.to, msg.to)
                if msg.text == "me":
                    sendMessage(msg.to, text=None, contentMetadata={'mid': msg.from_}, contentType=13)
                if msg.text == "gift":
                    sendMessage(msg.to, text="gift sent", contentMetadata=None, contentType=9)
                else:
                    pass
            else:
                pass
        if msg.toType == 2:
            if msg.contentType == 16:
                msg.text = "post URL\n" + msg.contentMetadata["postEndUrl"]
                sendMessage(msg.to,msg.text)
            if msg.contentType == 13:
                sendMessage(msg.to, "你的Line用戶識別碼:" + msg.contentMetadata["mid"])
                contact = client.getContact(msg.contentMetadata["mid"])
                try:
                    cu = client.channel.getCover(msg.contentMetadata["mid"])
                except:
                    cu = ""
                sendMessage(msg.to, "[名稱]:\n" + contact.displayName + "\n[mid]:\n" + msg.contentMetadata["mid"] + "\n[個性簽名]:\n" + contact.statusMessage + "\n[頭貼網址]:\nhttp://dl.profile.line-cdn.net/" + contact.pictureStatus + "\n[主頁照片網址]:\n" + str(cu))
            if msg.contentType == 0:
                if msg.text == "mid":
                    sendMessage(msg.to, msg.from_)
                if msg.text == "gid":
                    sendMessage(msg.to, msg.to)
                if msg.text == "Ginfo":
                    group = client.getGroup(msg.to)
                    try:
                        gCreator = group.creator.displayName
                    except:
                        gCreator = "Error"
                    md = "[群組名子]\n" + group.name + "\n\n[gid]\n" + group.id + "\n[群組作者]\n" + gCreator + "\n\n[群組頭像]\nhttp://dl.profile.line-cdn.net/" + group.pictureStatus
                    if group.preventJoinByTicket is False: md += "\n\n邀請網址: 開放中\n"
                    else: md += "\n\n邀請網址: 關閉中\n"
                    if group.invitee is None: md += "\n成員人數: " + str(len(group.members)) + "人\n\n邀請中: 0人"
                    else: md += "\n成員人數: " + str(len(group.members)) + "人\n邀請中: " + str(len(group.invitee)) + "人"
                    sendMessage(msg.to,md)
                if "gname:" in msg.text:
                    key = msg.text[22:]
                    group = client.getGroup(msg.to)
                    group.name = key
                    client.updateGroup(group)
                    sendMessage(msg.to,"Group Name"+key+"Canged to")
                if msg.text == "url":
                    sendMessage(msg.to,"http://line.me/R/ti/g/" + client._client.reissueGroupTicket(msg.to))
                if msg.text == "open":
                    group = client.getGroup(msg.to)
                    if group.preventJoinByTicket == False:
                        sendMessage(msg.to, "開放中喔(*´･ω･*)")
                    else:
                        group.preventJoinByTicket = False
                        client.updateGroup(group)
                        sendMessage(msg.to, "已開啟網址")
                if msg.text == "close":
                    group = client.getGroup(msg.to)
                    if group.preventJoinByTicket == True:
                        sendMessage(msg.to, "關閉中喔(*´･ω･*)")
                    else:
                        group.preventJoinByTicket = True
                        client.updateGroup(group)
                        sendMessage(msg.to, "已關閉網址")
                if "kick:" in msg.text:
                    key = msg.text[5:]
                    client.kickoutFromGroup(msg.to, [key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" 掰掰囉")
                if "nk:" in msg.text:
                    key = msg.text[3:]
                    group = client.getGroup(msg.to)
                    Names = [contact.displayName for contact in group.members]
                    Mids = [contact.mid for contact in group.members]
                    if key in Names:
                        kazu = Names.index(key)
                        sendMessage(msg.to, "Bye")
                        client.kickoutFromGroup(msg.to, [""+Mids[kazu]+""])
                        contact = client.getContact(Mids[kazu])
                        sendMessage(msg.to, ""+contact.displayName+" 掰掰囉")
                    else:
                        sendMessage(msg.to, "wtf?")
                if msg.text == "Cancel":
                    group = client.getGroup(msg.to)
                    if group.invitee is None:
                        sendMessage(op.message.to, "咦? 沒有人被邀請")
                    else:
                        gInviMids = [contact.mid for contact in group.invitee]
                        client.cancelGroupInvitation(msg.to, gInviMids)
                        sendMessage(msg.to, "已取消了" + str(len(group.invitee)) + "人")
                if "invite:" in msg.text:
                    key = msg.text[-33:]
                    client.findAndAddContactsByMid(key)
                    client.inviteIntoGroup(msg.to, [key])
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+" I invited you")
                if msg.text == "me":
                    M = Message()
                    M.to = msg.to
                    M.contentType = 13
                    M.contentMetadata = {'mid': msg.from_}
                    client.sendMessage(M)
                if "show:" in msg.text:
                    key = msg.text[-33:]
                    sendMessage(msg.to, text=None, contentMetadata={'mid': key}, contentType=13)
                    contact = client.getContact(key)
                    sendMessage(msg.to, ""+contact.displayName+"'s contact")
                if msg.text == "Time":
                    sendMessage(msg.to, "台灣標準時刻：" + datetime.datetime.today().strftime('%Y年%m月%d日 %H:%M:%S') + "is")
                if msg.text == "Gift":
                    sendMessage(msg.to, text="gift sent", contentMetadata=None, contentType=9)
                if msg.text == "Point":
                    sendMessage(msg.to, "開始紀錄已讀不回♪\n小心喔 已讀不回者♪")
                    try:
                        del wait['readPoint'][msg.to]
                        del wait['readMember'][msg.to]
                    except:
                        pass
                    wait['readPoint'][msg.to] = msg.id
                    wait['readMember'][msg.to] = ""
                    wait['setTime'][msg.to] = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                    wait['ROM'][msg.to] = {}
                    print wait
                if msg.text == "Read":
                    if msg.to in wait['readPoint']:
                        if wait["ROM"][msg.to].items() == []:
                            chiya = ""
                        else:
                            chiya = ""
                            for rom in wait["ROM"][msg.to].items():
                                print rom
                                chiya += rom[1] + "\n"

                        sendMessage(msg.to, "抓到了(*′△`)\n看到訊息者 %s\n--------------------\n\n已讀不回者\n%s\n此訊息偵測時間:\n[%s]"  % (wait['readMember'][msg.to],chiya,setTime[msg.to]))
                    else:
                        sendMessage(msg.to, "An already read point has not been set.\n「Point」you can send ♪ read point will be created ♪")
                if msg.text == "Sp":
                    start = time.time()
                    sendMessage(msg.to, "NyaPass~ 喵PASS~(*′△`)ﾉ 檢查中...")
                    elapsed_time = time.time() - start
                    sendMessage(msg.to, "%sseconds" % (elapsed_time))                
                if msg.text == "Cleanse":
                    print "ok"
                    _name = msg.text.replace("Cleanse","")
                    gs = client.getGroup(msg.to)
                    sendMessage(msg.to,"Kick By 屁孩大聯盟專業翻群\nsaya a beat Touhou Gensoukyou grup and rata karena bot ini, 東方Project,Touhou Project,Project Shrine Maiden\nNyaPass")
                    targets = []
                    for g in gs.members:
                        if _name in g.displayName:
                            targets.append(g.mid)
                    if targets == []:
                        sendMessage(msg.to,"error")
                    else:
                        for target in targets:
                            try:
                                klist=[client]
                                kicker=random.choice(klist)
                                kicker.kickoutFromGroup(msg.to,[target])
                                print (msg.to,[g.mid])
                            except:
                                sendText(msg.to,"error")
                if msg.text == "Tagall":
                    group = client.getGroup(msg.to)
                    nama = [contact.mid for contact in group.members]
                    cb = ""
                    cb2 = ""
                    strt = int(0)
                    akh = int(0)
                    for md in nama:
                        akh = akh + int(5)
                        cb += """{"S":"""+json.dumps(str(strt))+""","E":"""+json.dumps(str(akh))+""","M":"""+json.dumps(md)+"},"""
                        strt = strt + int(6)
                        akh = akh + 1
                        cb2 += "@nrik\n"
                    cb = (cb[:int(len(cb)-1)])
                    msg.contentType = 0
                    msg.text = cb2
                    msg.contentMetadata ={'MENTION':'{"MENTIONEES":['+cb+']}','EMTVER':'4'}
                    try:
                        client.sendMessage(msg)
                    except Exception as error:
                   	    print error 
                else:
                    pass
        else:
            pass

    except Exception as e:
        print e
        print ("\n\nSEND_MESSAGE\n\n")
        return

tracer.addOpInterrupt(25,SEND_MESSAGE)

while True:
    tracer.execute()
