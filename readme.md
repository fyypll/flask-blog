#### MAPLE博客相关说明

1. ##### 环境配置

   运行环境要求：`mysql` 版本5.7（数据库格式为`utf8mb4`）、`python` 版本3.7

   
   可在 `mysql` 命令行中用以下命令创建一个名为 `flaskblog` 且格式为 `utf8mb4` 的数据库：

   ```mysql
   create database flaskblog default character set utf8mb4 collate utf8mb4_unicode_ci;
   ```

   数据库相关配置信息可在 `config.py` 文件中修改

   

   创建并进入python虚拟环境，安装环境依赖

   ```shell
   pip install -r requirements.txt
   ```

   

   执行如下命令完成数据库迁移

   ```shell
   flask db migrate -m '提交信息'
   ```

   

   执行如下命令将更改同步到数据库中，此时，你就可以看到数据库中出现了相关的表了

   ```shell
   flask db upgrade
   ```

   

2. ##### 程序的部署

   系统为 `Centos7` ，为了方便管理，用的宝塔面板。在面板中安装 `python项目管理器` 、 `nginx `、 `mysql` 、安装相应的 `python3.7` 版本

   在宝塔面板 `网站` 处点击添加站点，然后点击 `设置` 进行如下配置

    `nginx` 配置

       # 监听端口
       listen 80;
       server_name 公网ip或域名;
       
       # 所有非静态文件请求转到wsgi服务
       location / {
       include uwsgi_params;
       # wsgi服务地址，用于nginx和wsgi通讯
       uwsgi_pass 127.0.0.1:18888;
       }

   ​    

   将程序上传到服务器，在`python项目管理器` 中安装好需要使用的 `python` 版本，然后点击添加项目，进行创建，然后选择你刚才上传的程序，选择 `python` 版本、框架选 `flask` 、启动方式选 `uwsgi` 、勾上 `安装模块依赖` （确保文件 `requirements.txt` 存在，否则无法安装依赖），然后确定即可开始部署，点击配置输入如下内容：

   `wsgi` 配置（ `uwsgi.ini` 文件）

       [uwsgi]
       # chdir — 项目所在的目录
       chdir=/www/wwwroot/maple
       # virtualenv — 虚拟环境目录
       virtualenv=/www/wwwroot/maple/maple_venv
       # myblog:app（启动文件和flask实例化的变量名）
       module=myblog:app
       # 启动文件
       wsgi-file=myblog.py
       callable=app
       # master进程管理其他进程，以上述配置例子，其中的uwsgi程都是master程的子程，如果kill master程，相于重启所有的uwsgi进程
       master=true
       # 进程量
       processes=4 
       # 线程量
       threads=2
       # 使程序在后台运行，并将日志打到指定的日志文件或者udp服器，日志文件自建
       # daemonize=/var/log/uwsgi/test.log
       # 其中socket是用uwsgi与nginx之通信的，所以两者要一致
       socket=127.0.0.1:18888
   
   
   
   点击启动即可开始运行项目
   
   然后访问 `nginx` 配置的：`server_name:listen` 即可访问运行的项目
   
   
   
   也可以在命令行手动启动项目，不过过程略微麻烦，首先需要进入虚拟环境，命令如下
   
   ```
   source 项目路径/项目名_venv/bin/activate
   ```
   
   
   
   比如我的就是
   
   ```
   source /www/wwwroot/maple/maple_venv/bin/activate
   ```
   
   

   然后你会发现命令行最左边信息会出现一个括号围起来的虚拟环境名称

   没激活虚拟环境时是这样的

   ```
   [root@ecs-sn3-medium-2-linux-20191122221125 maple]#
   ```
   
   

   激活虚拟环境后是这样的
   ```
   (maple_venv) [root@ecs-sn3-medium-2-linux-20191122221125 maple]#
   ```
   
   

   激活虚拟环境后运行如下命令启动服务
   ```
   uwsgi --ini uwsgi.ini
   ```

​	

3. ##### 遇到的问题

   网页成功加载出来了，但是网页页面样式和图片丢失

   通过查看加载出来的网页源代码的样式链接点击后访问的地址可知访问静态资源的地址是 `ip/static/静态资源文件名`

   但是这样访问为 `404` ，找不到资源，经过实验需要 `ip/app/static/静态资源文件名` 才能正常访问静态资源，通过 `nginx` 配置静态资源目录失败

   

   解决办法：

   ~~1.配置 `nginx` 静态资源路径方式失效，原因未知~~

   ~~2.目前解决办法是将 `app` 目录中的static文件夹剪切到项目根目录（与 `app` 文件夹同一级），样式与图片才成功加载~~

   3.上面方法有问题，字体样式会缺失，解决办法是创建名为 `static` 的软连接，将其指定到静态资源所在目录 `app/static` ，然后将这个软连接放在项目根目录即可完美解决

   

   **注：**

   系统管理员默认为第一个注册的账号，也就是 `用户id=1` 的账号