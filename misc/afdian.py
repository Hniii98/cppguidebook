from collections import namedtuple
import os
import requests
import time
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class User(namedtuple('User', ['name', 'avatar', 'all_sum_amount', 'remark'])):
    pass

class Order(namedtuple('Order', ['remark'])):
    pass

manual_sponsors = [
    User('等疾风', 'https://i0.hdslb.com/bfs/face/b658b5ca52f41e53321d04f978be6784ca6f8687.jpg', '1000.00', '小彭老师加油，希望给个赞助位'),
    User('只喝白开水', 'https://i2.hdslb.com/bfs/face/821b88a24c1319d1fb51b3854884e2f829855c75.jpg', '100.00', '确实快了 30 倍[赞]'),
    User('包乾', '', '26.90', ''),
    User('柿柿如意', '', '20.00', '请小彭老师喝奶茶'),
    User('Starry', '', '100.00', '小彭老师加油！'),
    User('阿哲', '', '100.00', '从小彭老师视频里学到太多'),
    User('Eureka', '', '20.00', '希望我能赚的多一点，之后发电也就多一点'),
    User('孙斌', '', '200.00', '06班孙斌，望越来越好'),
    User('nullptr', 'https://i0.hdslb.com/bfs/face/effa1ec9bb0f5d09ed415da75129aca9d16092ac.jpg', '23.30', '小彭老师千古，伟大无需多言'),
    User('Fred Song', '', '25.00', '小彭老师早点休息'),
    User('**振', '', '20.00', ''),
    User('**伟', '', '20.00', ''),
    User('**枫', '', '26.90', ''),
]

def afd_query(which, **params):
    user_id = '6256dedc1af911eebf8152540025c377'
    token = os.environ['AFDIAN_TOKEN']
    ts = int(time.time())
    params = json.dumps(params)
    sign = hashlib.md5(f'{token}params{params}ts{ts}user_id{user_id}'.encode('utf-8')).hexdigest()
    res = requests.get(f'https://afdian.net/api/open/{which}', params={
        'user_id': user_id,
        'params': params,
        'ts': ts,
        'sign': sign,
    }).json()
    assert res['ec'] == 200, res
    return res['data']

def afd_paged_query(which):
    i = 1
    while True:
        page = afd_query(which, page=i)
        n = page['total_page']
        for item in page['list']:
            yield item
        if i >= n:
            break
        i += 1

def afd_query_orders():
    order_lut = {}
    for order in afd_paged_query('query-order'):
        print(f'{order['user_id']}: {order['remark']}')
        order_lut[order['user_id']] = Order(order['remark'])
    return order_lut

def afd_query_sponsors():
    res = []
    order_lut = afd_query_orders()
    for user in afd_paged_query('query-sponsor'):
        user_id = user['user']['user_id']
        last_order = order_lut.get(user_id, None)
        if last_order:
            remark = last_order.remark
        else:
            remark = ''
        user_obj = User(user['user']['name'],
                        user['user']['avatar'],
                        user['all_sum_amount'],
                        remark)
        res.append(user_obj)
    return res

def afd_gen_thank_list():
    sponsors = afd_query_sponsors()
    sponsors += manual_sponsors
    max_x = 30
    max_y = 30
    stride_x = 450
    stride_y = 120
    limit_y = 720
    max_max_y = max_y
    for user in sponsors:
        max_y += stride_y
        if max_y + 10 >= limit_y:
            max_max_y = max(max_max_y, max_y)
            max_y = 30
            max_x += stride_x
    max_max_y = max(max_max_y, max_y)
    max_max_x = max_x + stride_x
    max_y += 10
    img = Image.new('RGB', (max_max_x, max_max_y), color='#19242e')
    x = 30
    y = 30
    total = 0
    for user in sponsors:
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('/usr/share/fonts/noto-cjk/NotoSansCJK-Medium.ttc', size=20)
        font_small = ImageFont.truetype('/usr/share/fonts/noto-cjk/NotoSerifCJK-Medium.ttc', size=13)
        if user.avatar:
            avatar = Image.open(BytesIO(requests.get(user.avatar).content))
        else:
            wx_path = f'/home/bate/下载/wx-{user.name.replace('/', '|')}.png'
            if os.path.exists(wx_path):
                avatar = Image.open(wx_path)
            else:
                this_dir = os.path.dirname(os.path.abspath(__file__))
                avatar = Image.open(os.path.join(this_dir, '../docs/img/favicon.ico'))
        avatar = avatar.resize((90, 90))
        img.paste(avatar, (x, y))
        draw.text((x + 100, y), f'{user.name}', fill='white', font=font)
        draw.text((x + 100, y + 30), f'￥{user.all_sum_amount}', fill='#aaaaaa', font=font)
        remark = user.remark
        if remark:
            remark = remark.rstrip('。').replace('.。', '，')
            draw.text((x + 100, y + 60), f'{remark}', fill='#779977', font=font_small)
        print(f'{user.name} ￥{user.all_sum_amount} {remark}')
        total += float(user.all_sum_amount)
        y += stride_y
        if y + 10 >= limit_y:
            y = 30
            x += stride_x
    print(total)
    return img

def main():
    img = afd_gen_thank_list()
    file = 'docs/img/thanks.png'
    img.save(file)
    os.system(f'display {file}')

if __name__ == '__main__':
    main()
