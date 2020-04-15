from datetime import datetime
from flask import request
from flask_login import current_user
from flask_paginate import get_page_parameter, Pagination
from app import app
from app.models import User


# 封装分页功能
# 参数：1.每页显示文章数 2.要切片(分页)的数据 3.进行json处理吗,字符串yes或者no
# 注意：to_json函数需要在表模型中设置过，方可使用
def fenye(per_page, datas, isjson):
    # 获取页码，若失败则取默认值1
    page = request.args.get(get_page_parameter(), type=int, default=1)
    total = len(datas)
    start = (page - 1) * per_page
    end = start + per_page
    # 分页模板使用的Boostrap版本，页码，总文章数，每页多少篇文章
    pagination = Pagination(bs_version=3, page=page, total=total, per_page=per_page)
    # 对数据进行切片(每per_page篇切一次)
    data_info = datas[slice(start, end)]
    final_data = []
    if isjson == 'json':
        # 将切片后的数据进行json化处理
        for data in data_info:
            # 使用类中的to_json函数进行处理
            final_data.append(data.to_json())
        return pagination, final_data
    elif isjson == 'nojson':
        return pagination, data_info
    return '最后一个参数只能是json或者nojson哦'


# 时间过滤器
@app.template_filter('time_filter')
def time_filter(time):
    if isinstance(time, datetime):
        now = datetime.now()
        # 两个时间相减，得到描述
        # print(time)
        timestamp = (now - time).total_seconds()
        if timestamp < 60:
            return '刚刚'
        elif timestamp < 60 * 60 and timestamp >= 60:
            minutes = timestamp / 60
            return "%s 分钟前" % int(minutes)
        elif timestamp >= 60 * 60 and timestamp < 60 * 60 * 24:
            hours = timestamp / (60 * 60)
            return "%s 小时前" % int(hours)
        elif timestamp >= 60 * 60 * 24 and timestamp < 60 * 60 * 24 * 30:
            days = timestamp / (60 * 60 * 24)
            return "%s 天前" % int(days)
        else:
            return time.strftime('%Y/%m/%d %H:%M')
    else:
        return time


# 获取当前登录用户头像和用户名
def getuser():
    user_info = User.query.filter_by(username=current_user.username).first_or_404()
    user = {
        'avatar': user_info.avatar(128),
        'username': user_info.username
    }
    return user
