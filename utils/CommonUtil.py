import hashlib
import re
import time
import urllib


class CommonUtil(object):

    def __init__(self):
        pass

    @staticmethod
    def makeMd5(param_string):
        md = hashlib.md5()
        md.update(param_string.encode())
        return md.hexdigest()

    @staticmethod
    def dict_get(dict, objkey, default):
        tmp = dict
        for k, v in tmp.items():
            if k == objkey:
                return v
            else:
                if (type(v).__name__ == 'dict'):
                    ret = CommonUtil.dict_get(v, objkey, default)
                    if ret is not default:
                        return ret
        return default

    @staticmethod
    def dict_byte_convert_string(byteDict):
        stringDict = {}
        for i in byteDict:
            key = bytes.decode(i)
            vales = bytes.decode(byteDict[i])
            stringDict[key] = vales
        return stringDict

    @staticmethod
    def sales_tip_2_sales(sales_tip):
        num = re.findall("[1-9]\d*\.\d*|0\.\d*[1-9]\d*$", sales_tip)
        if not num:
            num = re.findall("[1-9]\d*|0", sales_tip)
            if not num:
                return None
        sales = num[0]
        if re.findall("万", sales_tip):
            sales = float(sales) * 10000
        return int(sales)

    @staticmethod
    def make_query_by_dict(parameters):
        string = ''
        if len(parameters) <= 0:
            return string
        xxx = []
        for (key, v) in parameters.items():
            xxx.append(key + "=" + urllib.parse.quote(v))
        string = '&'.join(xxx)
        return string
