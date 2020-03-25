# 网站
from pyecharts_javascripthon.api import TRANSLATOR
from flask import Flask, render_template
# 数据
import itchat
import codecs
import json
import os
import random
import math
import PIL.Image as Image
import pandas as pd
from pyecharts import Bar,Pie,Map,WordCloud 
from senti_python import sentiment_score_list, sentiment_score  # 导入情感分析库的两个方法
# 容器类 
from collections import Counter
import jieba.analyse
from collections import defaultdict

REMOTE_HOST = "https://pyecharts.github.io/assets/js"

app = Flask(__name__)

# -----------------------------------------------------绘制----------------------------------start
# 绘制地图  有些bug  需要加包
# http://pyecharts.org/#/zh-cn/charts_base?id=map（地图）
# http://pyecharts.org/#/zh-cn/customize_map
# pip install echarts-countries-pypkg
# pip install echarts-china-provinces-pypkg
# pip install echarts-china-cities-pypkg
# pip install echarts-china-counties-pypkg
# pip install echarts-china-misc-pypkg
# pip install echarts-cities-pypkg
def drawMap(name,rank):
    map = Map(title='微信好友区域分布图', width=1200, height=600, title_pos='center')
    map.add(
        '',name,rank,
        maptype = 'china', # 地图范围
        is_visualmap = True, # 是否开启鼠标缩放漫游等
        is_label_show = True # 是否显示地图标记
    )
    return map

# 绘制饼图 
def drawPie(name,rank):
    pie = Pie('性别比例图', width=1200, height=600, title_pos='center')
    pie.add(
        '',
        name,rank,
        is_label_show = True, # 是否显示标签
        label_text_color = None, # 标签颜色
        legend_orient = 'vertical', # 图例是否垂直
        legend_pos = 'left'
    )
    return pie

# 绘制柱状图 
def drawBar(name,rank):
    bar = Bar(title='省份分布柱状图',width=1200,height=600,title_pos='center')
    bar.add(
        '', # 注解label属性
        name, # 横
        rank # 纵
    ) 
    return bar

# 绘制个性签名词云
def drawWorldCloud(name,rank):
    cloud = WordCloud('微信好友签名词云图', width=1200, height=600, title_pos='center')
    cloud.add(
        ' ',name,rank,
        shape='circle',
        background_color='white',
        max_words=200
    )
    return cloud

# 获取头像
def headImg():
    itchat.login()
    friends = itchat.get_friends(update=True)
    # itchat.get_head_img() 获取到头像二进制，并写入文件，保存每张头像
    for count, f in enumerate(friends):
        # 根据userName获取头像
        img = itchat.get_head_img(userName=f["UserName"])
        imgFile = open("./img/" + str(count) + ".jpg", "wb")
        imgFile.write(img)
        imgFile.close()

# 微信好友头像拼接图
def createImg():
    x = 0
    y = 0
    imgs = os.listdir("./img")
    random.shuffle(imgs)
    # 创建740*740的图片用于填充各小图片
    newImg = Image.new('RGBA', (740, 740))
    # 以740*740来拼接图片，math.sqrt()开平方根计算每张小图片的宽高，
    width = int(math.sqrt(740 * 740 / len(imgs)))
    # 每行图片数
    numLine = int(740 / width)

    for i in imgs:
        img = Image.open("./img/" + i)
        # 缩小图片
        img = img.resize((width, width), Image.ANTIALIAS)
        # 拼接图片，一行排满，换行拼接
        newImg.paste(img, (x * width, y * width))
        x += 1
        if x >= numLine:
            x = 0
            y += 1

    newImg.save("./static/all.png")

# 数据存储方法，为了防止编码不统一的情况，使用codecs来进行打开 
def saveFriends(friendsList):
    outputFile = './friends.json'
    with codecs.open(outputFile,'w',encoding='utf-8') as jsonFile: 
        # 默认使用ascii，为了输出中文将参数ensure_ascii设置成False 
        jsonFile.write(json.dumps(friendsList,ensure_ascii=False)) 

def getFriends(inputFile):
    with codecs.open(inputFile,encoding='utf-8') as f:
        friendsList = json.load(f)
        return friendsList

# 利用jieba模块提取出关键词并计算其权重，利用了TF-IDF算法 
def extractTag(text,tagsList):
    if text:
        tags = jieba.analyse.extract_tags(text)
        for tag in tags:
            tagsList[tag] += 1

# 实现将counter数据结构拆分成两个list，再传给pyecharts
def counter2list(_counter):
    nameList,countList = [],[]
    for counter in _counter:
        nameList.append(counter[0])
        countList.append(counter[1])
    return nameList,countList 

def dict2list(_dict):
    nameList, countList = [], []
    for key,value in _dict.items():
        nameList.append(key)
        countList.append(value)
    return nameList, countList

# -----------------------------------------------------绘制----------------------------------end


# 统一裁剪函数
def tongyicaijian(_bar, javascript_snippet):
    return render_template(
        "text.html",
        chart_id=_bar.chart_id,
        host=REMOTE_HOST,
        renderer=_bar.renderer,
        my_width="100%",
        my_height=600,
        custom_function=javascript_snippet.function_snippet,
        options=javascript_snippet.option_snippet,
        script_list=_bar.get_js_dependencies(),
    )

provinceList = ''
rankList = 0

# 主页路由
@app.route("/")
def index():
    return render_template("index.html", friendList=friendList, **numss)

# 地图地域分布路由
@app.route("/ditu")
def ditu():
    _bar = drawMap(provinceList, rankList)
    javascript_snippet = TRANSLATOR.translate(_bar.options)
    return tongyicaijian(_bar, javascript_snippet)

# 性别比例路由
@app.route("/sex")
def sex():
    sexList,percentList = dict2list(sexDict)
    _bar = drawPie(sexList, percentList)
    javascript_snippet = TRANSLATOR.translate(_bar.options)
    return tongyicaijian(_bar, javascript_snippet)

# 省份分布柱状图路由
@app.route("/shengfen")
def shengfen():
    sexList,percentList = dict2list(sexDict)
    _bar = drawBar(provinceList, rankList)
    javascript_snippet = TRANSLATOR.translate(_bar.options)
    return tongyicaijian(_bar, javascript_snippet)

# 词云路由
@app.route("/ciyun")
def ciyun():
    sexList,percentList = dict2list(sexDict)
    tagsList,rankList = counter2list(signatureCounter.most_common(200))
    _bar = drawWorldCloud(tagsList, rankList)
    javascript_snippet = TRANSLATOR.translate(_bar.options)
    return tongyicaijian(_bar, javascript_snippet)

# 头像拼图路由
@app.route("/headimg")
def headimg():
    return render_template("headimg.html")

if __name__ == '__main__':

    # 性别在itchat接口获取的数据中显示的是0，1，2三种我们使用一个字典将其映射为男、女、其他
    sexList = {'0': '其他', '1': '男', '2': '女'}
    # 自动登陆
    itchat.auto_login()
    # 利用API获取朋友列表
    friends = itchat.get_friends(update=True)

    # 获取好友全部数字信息-------------------------------start
    number_of_friends = len(friends)  # 总好友数
    df_friends = pd.DataFrame(friends)
    def get_count(Sequence):
        counts = defaultdict(int) #初始化一个字典
        for x in Sex:
            counts[x] += 1
        return counts

    Sex = df_friends.Sex
    Sex_count = get_count(Sex) #  性别数

    Sex_count = Sex.value_counts() # defaultdict(int, {0: 31, 1: 292, 2: 245})
    Sex_count.plot(kind = 'bar')

    Province = df_friends.Province 
    Province_count = Province.value_counts() 
    Province_count = Province_count[Province_count.index!=''] # 有一些好友地理信息为空，过滤掉这一部分人。

    City = df_friends.City #[(df_friends.Province=='北京') | (df_friends.Province=='四川')] 
    City_count = City.value_counts() 
    City_count = City_count[City_count.index!='']

    numss = {
        "number_of_friends": number_of_friends,
        "Sex_count1": Sex_count[1],
        "Sex_count2": Sex_count[2],
        "Sex_count0": Sex_count[0],
        "Province_count_index0": Province_count.index[0],
        "Province_count0": Province_count[0],
        "Province_count_index1": Province_count.index[1],
        "Province_count1": Province_count[1],
        "Province_count_index2": Province_count.index[2],
        "Province_count2": Province_count[2],
        "City_count_index0": City_count.index[0],
        "City_count0": City_count[0],
        "City_count_index1": City_count.index[1],
        "City_count1": City_count[1],
        "City_count_index2": City_count.index[2],
        "City_count2": City_count[2],
        "City_count_index3": City_count.index[3],
        "City_count3": City_count[3],
        "City_count_index4": City_count.index[4],
        "City_count4": City_count[4],
        "City_count_index5": City_count.index[5],
        "City_count5": City_count[5]
    }
    # 获取好友全部数字信息---------------------------------end

    # 绘制头像拼图
    headImg()
    createImg()

    friendsList = []
    for friend in friends:
        # 将friends提取出有用数据并存放在字典中
        item = {}
        item['昵称'] = friend['NickName']
        item['性别'] = sexList[str(friend['Sex'])]
        item['省份'] = friend['Province']
        item['城市'] = friend['City']
        item['个性签名'] = friend['Signature']
        item['头像'] = friend['UserName']
        item['备注'] = friend['RemarkName']

        try:
            if friend['Signature'].strip() != "":
                Pos_1 = sentiment_score(sentiment_score_list(friend['Signature']))[0][0]
                Neg_1 = sentiment_score(sentiment_score_list(friend['Signature']))[0][1]

                # print("{0}：{1}".format(Pos_1, Neg_1))

                if Pos_1 > Neg_1:
                    # item['情感分析'] = Pos_1 # + "：" + Neg_1 + " ---> 属于积极情感(或正能量)"
                    item['情感分析'] = "{0} : {1} ---> 属于积极情感(或正能量)".format(Pos_1, Neg_1)
                    # print("{0} : {1} ---> 属于积极情感(或正能量)".format(Pos_1, Neg_1))
                elif Pos_1 == Neg_1:
                    # item['情感分析'] = Pos_1 # + "：" + Neg_1 + " ---> 属于消极情感(或负能量)"
                    item['情感分析'] = "{0} : {1} ---> 无法判断(或无法判断褒贬义)".format(Pos_1, Neg_1)
                    # print("{0} : {1} ---> 无法判断".format(Pos_1, Neg_1))
                else:
                    # item['情感分析'] = Pos_1 # + "：" + Neg_1 + " ---> 属于消极情感(或负能量)"
                    item['情感分析'] = "{0} : {1} ---> 属于消极情感(或负能量)".format(Pos_1, Neg_1)
                    # print("{0} : {1} ---> 属于消极情感(或负能量)".format(Pos_1, Neg_1))
            else:
                item['情感分析'] = "null"
                # print("null")
        except IndexError:
            print("============以下为分析出错的签名 不用管============")
            print(friend['Signature'])
            print("===================================================")

        friendsList.append(item)

    # 保存好友列表的json信息
    saveFriends(friendsList)
    # 读取friends.json中的数据
    inputFile = './friends.json'
    friendList = getFriends(inputFile)

    # 需要统计的字段使用counter数据类型存储
    provinceCounter = Counter()
    sexDict = {'男':0,'女':0,'其他':0}
    signatureCounter = Counter()

    for friend in friendList:
        if friend['省份'] != '':
            provinceCounter[friend['省份']] += 1
        sexDict[friend['性别']] += 1
        extractTag(friend['个性签名'],signatureCounter)

    # 统计出排名前16的省份
    provinceList,rankList = counter2list(provinceCounter.most_common(15))

    # 为防止网页自己频繁自动刷新，要改为False，因为自动刷新会重新登录微信
    app.run(debug=False)