mysql版本5.7

python版本3.7.4

创建数据库，格式为utf8mb4

`create database flaskblog default character set utf8mb4 collate utf8mb4_unicode_ci;`

数据库配置文件在config.py文件

配置完成数据库后，执行
`flask db init`
会生成migrations文件夹与相关文件(若该文件夹已存在则需先删除)

执行
`flask db migrate -m '提交信息'`
将数据库结构更新

执行
`flask db upgrade`
将更改同步到数据库中，此时，你就可以看到数据库中出现了相关的表了

安装环境依赖
`pip install -r requirements.txt`


关于部署到服务器
用宝塔面板，安装python包管理器，安装好nginx，安装相应的python3.7版本


nginx配置

    listen 80;
    server_name 公网ip或域名;
    
    # 所有非静态文件请求到flask服务器
    location / {
        include uwsgi_params;
        # wsgi服务地址，用于nginx和wsgi通讯
        uwsgi_pass 127.0.0.1:18888;
    }
 
 
 wsgi配置
 

    [uwsgi]
    # chdir — 目所在的目
    chdir=/www/wwwroot/maple
    # virtualenv — 目境的目
    virtualenv=/www/wwwroot/maple/maple_venv
    # 的model 
    # start:app
    module=myblog:app
    # 文件
    wsgi-file=myblog.py
    callable=app
    #一master程管理其他程，以上述配置例，其中的4uwsgi程都是master程的子程，如果killmaster程，相于重所有的uwsgi程
    master=true
    #程量
    processes=4 
    #程量
    threads=2
    ###使程在后台行，并日志打到指定的日志文件或者udp服器，日志文件自建
    #daemonize=/var/log/uwsgi/test.log
    #其中socket是用uwsgi与nginx之通信的，所以两者要一致
    socket=127.0.0.1:18888
    

遇到的问题：

网页成功加载出来了，但是静态资源并没有加载出来（样式丢失）

通过查看加载出来的网页源代码的样式链接点击后访问的地址可知访问静态资源的地址是ip/static

但是这样访问为404，找不到资源，经过实验需要ip/app/static才能正常访问静态资源，通过nginx配置静态资源目录失败

目前解决办法是将app目录中的static文件夹剪切到项目根目录（与app文件夹同一级），样式与图片才成功加载

