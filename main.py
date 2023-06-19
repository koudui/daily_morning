import json
from datetime import date, datetime
import math
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatMessage, WeChatTemplate
import requests
import os
import random

# 自定义相关数据
today = datetime.now()  # 获取当前日期，用于生日、特殊日子等天数判断
special_day = os.environ['START_DATE']
birthday = os.environ['BIRTHDAY']
city = os.environ['CITY']

# 微信公众号相关配置
app_id = os.environ["APP_ID"]
app_secret = os.environ["APP_SECRET"]
user_id = os.environ["USER_ID"]  # 需要发送消息的微信用户id
template_id = os.environ["TEMPLATE_ID"]  # 发送消息的模板id


# 获取经纬度
def get_location():
    url = "https://assets.msn.cn/service/v1/news/users/me/locations?apikey=1hYoJsIRvPEnSkk0hlnJF2092mHqiz7xFenIFKa9uc&activityId=6C0FF622-C725-4291-82AA-BCBF959A8090&ocid=pdp-peregrine&cm=zh-cn&it=app&user=m-096A3A943E556919186728683F3368F3&scn=APP_ANON&autodetect=true"
    res = requests.get(url).text
    if len(res) == 0:
        return ''
    return json.loads(res)[0].get('latitude'), json.loads(res)[0].get('longitude')


def get_weather():
    url = "https://assets.msn.cn/service/segments/recoitems/weather?apikey=UhJ4G66OjyLbn9mXARgajXLiLw6V75sHnfpU60aJBB&activityId=2E5B36CE-DEAC-4BA6-AD15-DC39131C490A&ocid=weather-peregrine&cm=zh-cn&it=app&user=m-096A3A943E556919186728683F3368F3&scn=APP_ANON&units=C&appId=4de6fc9f-3262-47bf-9c99-e189a8234fa2&wrapodata=false&includemapsmetadata=true&cuthour=true&getCmaAlert=true&filterRule=card&includenowcasting=true&nowcastingapi=2&distanceinkm=0&regionDataCount=20&orderby=distance&days=5&pageOcid=anaheim-ntp-peregrine&source=undefined_csr&hours=13&fdhead=prg-1sw-wxprate&contentcount=3&region=cn&market=zh-cn&locale=zh-cn&lat=30.57226&lon=104.06651"
    res = requests.get(url).text  # 获取响应数据
    res = json.loads(res)  # 解析json数据
    res = json.loads(res[0]['data'])  # 存在嵌套，需要解析json
    # print(res)
    current_weather = res.get('responses')[0].get('weather')[0].get('current')  # 当天天气
    # 当天天气分小时展示
    # print(res.get('responses')[0].get('weather')[0].get('forecast').get('days')[0].get('hourly'))
    print("当前天气：", current_weather)

    print(datetime.now())
    return {
        'weather': current_weather.get('cap'),
        'temp': current_weather.get('temp'),
    }


def get_weather_text():
    weather_data = get_weather()
    if '晴' in weather_data.get('weather') or weather_data.get('temp') >= 30:
        info = '快把防晒衣穿起来~'
    elif '雨' in weather_data.get('weather'):
        info = '别忘了带雨伞哦~'
    elif weather_data.get('temp') <= 15:
        info = '天凉了，记得添件衣服~'
    text = '%s天气%s，温度%s°C，%s' % (city, weather_data.get('weather'), weather_data.get('temp'), info)
    return text


# 判断纪念日天数
def get_special_day():
    delta = today - datetime.strptime(special_day, "%Y-%m-%d")
    return '我们已经相守%d天，以后还要继续走下去' % delta.days


# 判断生日天数
def get_birthday():
    next_day = datetime.strptime(str(date.today().year) + "-" + birthday, "%Y-%m-%d")
    if next_day < datetime.now():
        next_day = next_day.replace(year=next_day.year + 1)
    if (next_day - today).days == 0:
        return '生日快乐！'
    else:
        return '再过%d天，就是你的生日啦' % (next_day - today).days


# 彩虹屁，获取随机文本
def get_words():
    words = requests.get("https://api.shadiao.pro/chp")
    if words.status_code != 200:
        return get_words()
    return words.json()['data']['text']


# 获取随机色彩
def get_random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


# 创建微信客户端
client = WeChatClient(app_id, app_secret)
wm = WeChatMessage(client)

data = {"love_days": {"value": get_special_day()}, "weather_text": {"value": get_weather_text()}, "birthday_left": {"value": get_birthday()}, "words": {"value": get_words(), "color": get_random_color()}}
print(data)
# 发送消息，给指定用户发送指定模板消息
user_ids = user_id.split(',')
for user in user_ids:
    res_data = wm.send_template(user, template_id, data)
    print(res_data)
