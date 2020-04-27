from datetime import datetime
from flask import request
from flask_login import current_user
from flask_paginate import get_page_parameter, Pagination
from app import app
from app.models import User
import random
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter


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


# 生成指定位数验证码字符(这里是4位)
def gene_text():
    return ''.join(random.sample(string.ascii_letters + string.digits, 4))


# 给验证码图片设置随机颜色
def rndColor():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))


# 给验证码图片添加干扰线
def draw_lines(draw, num, width, height):
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)


# 生成验证码图形
def get_verify_code():
    code = gene_text()
    # 图片大小
    width, height = 110, 40
    # 新图片对象
    im = Image.new('RGB', (width, height), 'white')
    # 字体
    font = ImageFont.truetype('app/static/arial.ttf', 30)
    # draw对象
    draw = ImageDraw.Draw(im)
    str = ''
    # 绘制字符串
    for item in range(4):
        draw.text((5 + random.randint(-3, 3) + 23 * item, 5 + random.randint(-3, 3)),
                  text=code[item], fill=rndColor(), font=font)
    # 划线
    draw_lines(draw, 2, width, height)
    # 高斯模糊
    im = im.filter(ImageFilter.GaussianBlur(radius=1.5))
    return im, code
