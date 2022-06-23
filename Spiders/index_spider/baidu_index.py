
import requests, json, datetime
import execjs
import pymongo

headers = {
    'Cookie': 'BIDUPSID=A064EBA49CA64964F88B52743806B495; PSTM=1596525581; BAIDUID=A064EBA49CA649644F4121BC8279A589:FG=1; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDUSS=Jqd0ZYV0U4cDVMaC1QN1hLYTMzNzVxMkNpT3BmcXZtLTNibEFqbkdUYnluMWhmRVFBQUFBJCQAAAAAAAAAAAEAAAAT0AIIw9XNxb79AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPISMV~yEjFfTG; CHKFORREG=596afd874a8833f0107889aefa40b953; bdindexid=td46en946rshbn1vlmbtjp3f61; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1597043125,1597112693; delPer=0; PSINO=1; H_PS_PSSID=32288_1462_32438_32380_32357_32327_31253_32350_32046_32395_32407_32446_32116_31322_32496_32481; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1597115336; RT="sl=c&ss=kdpc6u90&tt=21dh&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&z=1&dm=baidu.com&si=3vz00eht9ii&ld=11ngf"'
}



data_url = 'http://index.baidu.com/api/SearchApi/index?area=0&word=[[%7B%22name%22:%22{}%22,%22wordType%22:1%7D]]&startDate={}&endDate={}' #dateformat as 2020-08-01
# %E5%B0%8F%E7%AB%99


password_url = 'http://index.baidu.com/Interface/ptbk?uniqid={}'


# decodejs
baidu_decode = execjs.compile('''
   function decrypt(password, data){
    let arr = password.split('');
    let dataArr = data.split('');
    let objPass = {};
    let notInNames = [];
    for (let i = 0; i < arr.length / 2; i++) {
        objPass[arr[i]] = arr[arr.length / 2 + i];
    }
    // 数据解密转换
    for (let i = 0; i < data.length; i++) {
        notInNames.push(objPass[dataArr[i]]);
    }
    // alert(notInNames.join(''));
    return notInNames.join('');
    } 
'''
)


MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27000
mydb = pymongo.MongoClient(MONGO_HOST,MONGO_PORT)
mycol = mydb['index']

# def get_list(search_word, startdate, enddata):


def getBaiduIndex(search_word, startdate, enddata):
    '''
    获取百度指数
    :param search_word: 字符串
    :param startdate: 2020-08-01
    :param enddata: 2020-09-01
    :return:
    '''
    url = data_url.format(search_word,startdate,enddata)
    # print(url)
    data_response = requests.get(url, headers=headers)
    raw_data = json.loads(data_response.text)
    if raw_data['status'] != 0:
        print('statuserror')
    else:
        data = raw_data['data']['userIndexes'][0]
        uniqid = raw_data['data']['uniqid']
        pwd_resposne = requests.get(password_url.format(uniqid),headers=headers)
        decode_pwd = json.loads(pwd_resposne.text)['data']
        # time_list
        enddate = data['all']['endDate']
        startdate = data['all']['startDate']
        et = str_to_date(enddate)
        st = str_to_date(startdate)
        # print(st,et)
        dtlist = get_datelist(st,et)
        # starting decode data
        baidu_index = {}
        alldata = data['all']['data']
        pcdata = data['pc']['data']
        wisedata = data['wise']['data']
        raw_all_trend = baidu_decode.call('decrypt', decode_pwd, alldata)
        all_trend_list = raw_all_trend.split(',')
        baidu_index['all_trend'] = dict(zip(dtlist, all_trend_list))
        # ------
        raw_pc_trend = baidu_decode.call('decrypt', decode_pwd, pcdata)
        pc_trend_list = raw_pc_trend.split(',')
        baidu_index['pc_trend'] = dict(zip(dtlist, pc_trend_list))
        # ------
        raw_wise_trend = baidu_decode.call('decrypt', decode_pwd, wisedata)
        wise_trend_list = raw_wise_trend.split(',')
        baidu_index['wise_trend'] = dict(zip(dtlist, wise_trend_list))
        baidu_index['_id'] = search_word
        return baidu_index


def str_to_date(dt):
    real_dt = datetime.datetime.strptime(dt, "%Y-%m-%d")
    return real_dt


def get_datelist(st, et):
    dtlist = []
    while st <= et:
        dtlist.append(st)
        st += datetime.timedelta(days=+1)
    dtlist = list(map(lambda dt: datetime.datetime.strftime(dt,'%Y-%m-%d'),dtlist))
    # print(dtlist)
    return dtlist

def save_to_mongo(data):
    try:
        mycol['baidu_index'].insert_one(data)
        print('baidu index data, keyword : {} has downloaded'.format(data['_id']))
    except Exception as e:
        mycol['baidu_index'].update_one()
        print(e)





today = datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d')
baidu_data = getBaiduIndex('北京疫情', '2020-07-01', today)
save_to_mongo(baidu_data)
print(baidu_data)