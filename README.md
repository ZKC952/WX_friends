[toc]
## 一、文件目录
```bash
├─ result
│  ├─ img                           # 好友头像存放文件夹
│  ├─ static                        # 静态文件夹
│  ├─ templates                     # 模板文件夹
│  │  ├─ headimg.html               # 头像拼图页面
│  │  ├─ index.html                 # 主页面
│  │  └─ text.html                  # 数据图展示页面
│  ├─ friends.json                  # 好友数据存放文件
│  ├─ README.html                   # 开发文档网页版
│  ├─ README.md                     # 开发文档源文件
│  ├─ requirements.txt              # 开发库集合
│  └─ run.py                        # 主文件/启动文件
```
## 二、安装包
```python
pip install -r requirements.txt
```
## 三、启动
```python
python test.py
```
- 在该文件夹执行命令后会弹出一个二维码图片，使用者用微信扫码登陆，然后需要等待一会
- 注：`win10`上能正常弹出二维码图片，`win7`可能不会，这个时候需要手动打开项目文件根目录下执行命令时生成`QR.png`图片扫码登陆
- 当终端输出`Use a production WSGI server instead.`，`WSGI`服务器跑起来之后，再在浏览器中输入`127.0.0.1:5000`访问
## 四、所用的部分技术以及库
```bash
bootstrap   # 前端框架
flask       # 后端框架
itchat      # 得到数据
json        # 存储数据
PIL         # 处理图像
pandas      # 数据分析
pyecharts   # 数据可视化
jieba       # 词云展示
```
## 五、总结
- 该项目实现了微信好友数据爬取，数据展示，具体如下：
    1. 好友数据表格展示
    2. 好友地图区域分布图
    3. 好友性别比例图
    4. 好友省份分布柱状图
    5. 好友签名词云/情感分析图
    6. 所有好友头像拼接图
- 具体内容浏览网站
- 注：浏览器建议用谷歌(特别是浏览开发文档网页版)


