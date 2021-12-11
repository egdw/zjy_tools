from typing import Counter, Sized
import requests
import json
from requests.models import to_key_val_list
import time
from requests.sessions import session
from requests.utils import to_native_string

header = {
    "Cookie":"acw_tc=707c9fdb16391151017412552e7ff02d5750cbf045cf58a28cc89159e1400f; verifycode=284500E736AC40144F61C1D2AC37B1C0@637747407022808052; Hm_lvt_a3821194625da04fcd588112be734f5b=1639115103; Hm_lpvt_a3821194625da04fcd588112be734f5b=1639115103; auth=0102258C7A3BA0BBD908FE259C260DF4BBD9080116680073006900620061007000710074006800690068006100780036006B006A003600640077007A006E00710000012F00FFEDC4C19AA13A5B38F796D1B0188F215E7AEE68C2; token=fqxiapqtypvf2ka2sigidw"
}

sess = requests.session()
# 查看目录
def ViewDirectory(courseOpenId,openClassId,cellId,moduleId):
    global sess,header
    data = {
            "courseOpenId":courseOpenId,
            "openClassId":openClassId,
            "cellId":cellId,
            "flag":"s",
            "moduleId":moduleId
    }
    b = sess.post("https://zjy2.icve.com.cn/api/common/Directory/viewDirectory",headers=header,data=data)
    data = json.loads(b.text)
    # print(data)
    if(data['code'] == -1):
        print(data['msg'])
        return None
    if data['code'] == -100:
        print("解决播放选择提醒！")
        data={
            "courseOpenId":courseOpenId,
            "openClassId":openClassId,
            "cellId":cellId,
            "cellName":data['currCellName'],
            "moduleId":moduleId
        }
        sess.post("https://zjy2.icve.com.cn/api/common/Directory/changeStuStudyProcessCellData",headers=header,data=data)
       
    return {
        "courseOpenId":data['courseOpenId'],
        "openClassId":data['openClassId'],
        "moduleId":data['moduleId'],
        "topicId":data['topicId'],
        "cellId":data['cellId'],
        "pageCount":data['pageCount'],
        "audioVideoLong":data['audioVideoLong'],
        "guIdToken":data['guIdToken'],
        "cellLogId":data['cellLogId'],
        "currPercent":data.get("currPercent",0),
        "lastPercent":data.get("lastPercent",0),
        "cellPercent":data['cellPercent'],
        "stuStudyNewlyPicCount":data['stuStudyNewlyPicCount'],
        "stuStudyNewlyTime":data['stuStudyNewlyTime']
    }

# ppt自动学习
def pptStudying(courseOpenId,openClassId,cellId,moduleId):
    global sess,header
    directory = ViewDirectory(courseOpenId,openClassId,cellId,moduleId)
    if(directory == None):
        return
    step = 1
    total_num = int(directory['pageCount'])+step
    # current = directory['stuStudyNewlyPicCount']
    current = 0

    while(current<=total_num):
        data = {
            "courseOpenId":courseOpenId,
            "openClassId":openClassId,
            "cellId":cellId,
            "cellLogId":"",
            "picNum":current,
            "studyNewlyTime":0,
            "studyNewlyPicNum":current,
            "token":directory['guIdToken'],
            "topicId":directory['topicId']
        }
        b = sess.post("https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog",headers=header,data=data)
        if current == total_num:
            break
        if current + step > total_num:
            current = total_num
        else:
            current = current + step
        time.sleep(0.05)
        print("当前进度：",(current/total_num)*100)
    directory = ViewDirectory(courseOpenId,openClassId,cellId,moduleId)
    print("查询最新完成进度:%s"%(directory["cellPercent"]))

# 视频学习
def videoStudying(courseOpenId,openClassId,cellId,moduleId):
    global sess,header
    directory = ViewDirectory(courseOpenId,openClassId,cellId,moduleId)
    if(directory == None):
        return
    step = 20
    total_num = int(directory['audioVideoLong'])
    current = directory['stuStudyNewlyTime']
    while(current<=total_num):
        data = {
            "courseOpenId":courseOpenId,
            "openClassId":openClassId,
            "cellId":cellId,
            "cellLogId":directory['cellLogId'],
            "picNum":0,
            "studyNewlyTime":current,
            "studyNewlyPicNum":0,
            "token":directory['guIdToken']
        }
        b = sess.post("https://zjy2.icve.com.cn/api/common/Directory/stuProcessCellLog",headers=header,data=data)
        if current == total_num:
            break
        if current + step > total_num:
            current = total_num
        else:
            current = current + step
        time.sleep(5)
        print("当前进度：",(current/total_num)*100)
    directory = ViewDirectory(courseOpenId,openClassId,cellId,moduleId)
    print("查询最新完成进度:%s"%(directory["cellPercent"]))

# 得到详细单元格数据
def getCellDetail(courseOpenId,openClassId,cell):
    global sess,header
    data = {
        "courseOpenId":courseOpenId,
        "openClassId":openClassId,
        "topicId":cell['id']
    }
    b = sess.post("https://zjy2.icve.com.cn/api/study/process/getCellByTopicId",headers=header,data=data)
    data = json.loads(b.text)
    if data['code'] == 1:
        return data

# 得到topic数据
def getTopic(courseOpenId,moduleId):
    global sess,header
    data = {
        "courseOpenId":courseOpenId,
        "moduleId":moduleId
    }
    b = sess.post("https://zjy2.icve.com.cn/api/study/process/getTopicByModuleId",headers=header,data=data)
    data = json.loads(b.text)
    if data['code'] == 1:
        return data

    
# 得到课程数据
def getCourseDetail(course):
    global sess,header
    courseOpenId = course['courseOpenId']
    openClassId = course['openClassId']
    data = {
        "courseOpenId":courseOpenId,
        "openClassId":openClassId
    }
    b = sess.post("https://zjy2.icve.com.cn/api/study/process/getProcessList",headers=header,data=data)
    data = json.loads(b.text)
    if data['code'] == 1:
        print("*****************项目*****************")
        # print(data['progress']['moduleList'])
        for project in data['progress']['moduleList']:
            print("项目名称:%s,项目学习进度:百分之%s"%(project['name'],project['percent']))
        print("*****************项目*****************")
        print("总单元数量:%s,已学习单元数：%s"%(data['openCourseCellCount'],data['stuStudyCourseOpenCellCount']))
        start = int(input("是否开始自动学习？0 False 1 True"))
        if start == 1:
            # 开始学习
            for project in data['progress']['moduleList']:
                topics = getTopic(courseOpenId,project['id'])
                for topic in topics['topicList']:
                    print("开始学习%s,获取子目录："%(topic['name']))
                    cells = getCellDetail(courseOpenId,openClassId,topic)
                    # try:
                    for cell in cells['cellList']:
                        if(int(cell['stuCellPercent']) == 100 or int(cell.get('stuCellFourPercent',0)) == 100):
                            print("检测发现%s，%s已经学习完成，跳过。"%(topic['name'],cell['cellName']))
                            continue
                        else:
                            if cell['categoryName'] == "ppt":
                                print("开始学习%s下的%s,当前进度为：%s"%(topic['name'],cell['cellName'],cell['stuCellPercent']))
                                pptStudying(courseOpenId,openClassId,cell['Id'],project['id'])
                            elif cell['categoryName'] == "子节点":
                                for cell_inline in cell['childNodeList']:
                                    if(int(cell_inline.get('stuCellPercent',0)) == 100 or int(cell_inline.get('stuCellFourPercent',0)) == 100):
                                        print("检测发现%s，%s已经学习完成，跳过。"%(topic['name'],cell['cellName']))
                                        continue
                                    if cell_inline['categoryName'] == "ppt":
                                        print("开始学习%s下的%s,当前进度为：%s"%(topic['name'],cell_inline['cellName'],cell_inline['stuCellPercent']))
                                        pptStudying(courseOpenId,openClassId,cell_inline['Id'],project['id'])
                                    elif cell_inline['categoryName'] == "视频":
                                        print("开始学习%s下的%s,当前进度为：%s"%(topic['name'],cell_inline['cellName'],cell_inline['stuCellFourPercent']))
                                        videoStudying(courseOpenId,openClassId,cell_inline['Id'],project['id'])
                            elif cell['categoryName'] == "视频":
                                print("开始学习%s下的%s,当前进度为：%s"%(topic['name'],cell['cellName'],cell['stuCellFourPercent']))
                                videoStudying(courseOpenId,openClassId,cell['Id'],project['id'])
                            else:
                                # 其他类型不处理
                                continue
                    # except Exception as e:
                        # print("学习%s下的%s出现异常"%(topic['name'],cell['cellName']),e)
    # print(b.text)


def checkCourse():
    global sess,header
    # 获取全部学习课程
    b = sess.post("https://zjy2.icve.com.cn/api/student/learning/getLearnningCourseList",headers=header)
    data = json.loads(b.text)
    if(data["code"] == 1):
        print("获取到了%s个课程内容"%(len(data['courseList'])))
        
        print("*****************课程*****************")
        for index,course in enumerate(data['courseList']):
            print(index,course['courseName'])
        print("*****************课程*****************")
        courseIndex =int(input("请输入你要学习的课程："))
        if courseIndex >=0 and courseIndex < len(data['courseList']):
            course = data['courseList'][courseIndex]
            getCourseDetail(course)
    else:
        print("Error：获取课程内容失败")    
    # print(b.text)

def checkLogin():
    global sess,header
    # 测试登陆是否成功
    b = sess.post("https://zjy2.icve.com.cn/api/student/Studio/index",headers=header)
    if json.loads(b.text)['code'] == 1:
        print("你好%s,登录成功"%(json.loads(b.text)['disPlayName']))
        return True
    else:
        print("登录失败")
        return False


if checkLogin():
    checkCourse()