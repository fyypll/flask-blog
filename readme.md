数据库配置文件在config.py文件

配置完成数据库后，执行
`flask db init`
会生成migrations文件夹与相关文件(若该文件夹已存在则需先删除)

执行
`flask db migrate -m '提交信息'`
将数据库结构更新

执行
`flask upgrade`
将更改同步到数据库中，此时，你就可以看到数据库中出现了相关的表了