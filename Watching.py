#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# 
########################################################################
 
"""
File: Watching.py
Author: AngelClover(AngelClover@aliyun.com)
Date: 2020/06/22 02:20:30
"""
#!/usr/bin/python
#coding=utf-8
import os
import re
import sys
import md5
import json
import copy
import getopt
import shutil
import logging
import urllib2

from time import sleep
from futu import *

import talib
import math
import datetime
import logging

class StockQuoteTest(StockQuoteHandlerBase):
    """
    获得报价推送数据
    """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* StockQuoteTest : %s" % content)
        return RET_OK, content


class CurKlineTest(CurKlineHandlerBase):
    """ kline push"""
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(CurKlineTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* CurKlineTest: error, msg: %s" % content)
        return RET_OK, content


class RTDataTest(RTDataHandlerBase):
    """ 获取分时推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(RTDataTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* RTDataTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* RTDataTest :%s \n" % content)
        return RET_OK, content


class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* TickerTest\n", content)
        return RET_OK, content


class OrderBookTest(OrderBookHandlerBase):
    """ 获得摆盘推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(OrderBookTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* OrderBookTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* OrderBookTest\n", content)
        return RET_OK, content


class BrokerTest(BrokerHandlerBase):
    """ 获取经纪队列推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, stock_code, contents = super(BrokerTest, self).on_recv_rsp(rsp_pb)
        if ret_code == RET_OK:
            bid_content = contents[0]
            ask_content = contents[1]
            # print("* BrokerTest code \n", stock_code)
            # print("* BrokerTest bid \n", bid_content)
            # print("* BrokerTest ask \n", ask_content)
        return ret_code


class SysNotifyTest(SysNotifyHandlerBase):
    """sys notify"""
    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, content = super(SysNotifyTest, self).on_recv_rsp(rsp_pb)

        if ret_code == RET_OK:
            main_type, sub_type, msg = content
            print("* SysNotify main_type='{}' sub_type='{}' msg='{}'\n".format(main_type, sub_type, msg))
        else:
            print("* SysNotify error:{}\n".format(content))
        return ret_code, content


class TradeOrderTest(TradeOrderHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            print("* TradeOrderTest content={}\n".format(content))

        return ret, content


class TradeDealTest(TradeDealHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeDealTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            print("TradeDealTest content={}".format(content))

        return ret, content



class MACD(object):
    """
    A simple MACD strategy
    """
    # API parameter setting
    api_svr_ip = '127.0.0.1'  # 账户登录的牛牛客户端PC的IP, 本机默认为127.0.0.1
    api_svr_port = 11111  # 富途牛牛端口，默认为11111
    unlock_password = "123456"  # 美股和港股交易解锁密码
    trade_env = TrdEnv.SIMULATE

    def __init__(self, stock, short_period, long_period, smooth_period,
                 observation):
        """
        Constructor
        """
        self.stock = stock
        self.short_period = short_period
        self.long_period = long_period
        self.smooth_period = smooth_period
        self.observation = observation
        self.quote_ctx, self.trade_ctx = self.context_setting()

    def close(self):
        self.quote_ctx.close()
        self.trade_ctx.close()

    def context_setting(self):
        """
        API trading and quote context setting
        :returns: trade context, quote context
        """
        if self.unlock_password == "":
            raise Exception("请先配置交易解锁密码! password: {}".format(
                self.unlock_password))

        quote_ctx = OpenQuoteContext(
            host=self.api_svr_ip, port=self.api_svr_port)

        if 'HK.' in self.stock:
            trade_ctx = OpenHKTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        elif 'US.' in self.stock:
            trade_ctx = OpenUSTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        else:
            raise Exception("不支持的stock: {}".format(self.stock))

        if self.trade_env == TrdEnv.REAL:
            ret_code, ret_data = trade_ctx.unlock_trade(
                self.unlock_password)
            if ret_code == RET_OK:
                print('解锁交易成功!')
            else:
                raise Exception("请求交易解锁失败: {}".format(ret_data))
        else:
            print('解锁交易成功!???')

        return quote_ctx, trade_ctx

    def handle_data(self):
        """
        handle stock data for trading signal, and make order
        """
        # 读取历史数据，使用sma方式计算均线准确度和数据长度无关，但是在使用ema方式计算均线时建议将历史数据窗口适当放大，结果会更加准确
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=self.observation)
                   ).strftime('%Y-%m-%d')
        end_dt = today.strftime('%Y-%m-%d')
        ret_code, prices, page_req_key = self.quote_ctx.request_history_kline(self.stock, start=pre_day, end=end_dt)
        if ret_code != RET_OK:
            print("request_history_kline fail: {}".format(prices))
            return

        # 用talib计算MACD取值，得到三个时间序列数组，分别为 macd, signal 和 hist
        # macd 是长短均线的差值，signal 是 macd 的均线
        # 使用 macd 策略有几种不同的方法，我们这里采用 macd 线突破 signal 线的判断方法
        macd, signal, hist = talib.MACD(prices['close'].values,
                                        self.short_period, self.long_period,
                                        self.smooth_period)

        # 如果macd从上往下跌破macd_signal
        if macd[-1] < signal[-1] and macd[-2] > signal[-2]:
            # 计算现在portfolio中股票的仓位
            ret_code, data = self.trade_ctx.position_list_query(
                trd_env=self.trade_env)

            if ret_code != RET_OK:
                raise Exception('账户信息获取失败: {}'.format(data))
            pos_info = data.set_index('code')

            cur_pos = int(pos_info['qty'][self.stock])
            # 进行清仓
            if cur_pos > 0:
                ret_code, data = self.quote_ctx.get_market_snapshot(
                    [self.stock])
                if ret_code != 0:
                    raise Exception('市场快照数据获取异常 {}'.format(data))
                cur_price = data['last_price'][0]
                ret_code, ret_data = self.trade_ctx.place_order(
                    price=cur_price,
                    qty=cur_pos,
                    code=self.stock,
                    trd_side=TrdSide.SELL,
                    order_type=OrderType.NORMAL,
                    trd_env=self.trade_env)
                if ret_code == RET_OK:
                    print('stop_loss MAKE SELL ORDER\n\tcode = {} price = {} quantity = {}'
                          .format(self.stock, cur_price, cur_pos))
                else:
                    print('stop_loss: MAKE SELL ORDER FAILURE: {}'.format(ret_data))

        # 如果短均线从下往上突破长均线，为入场信号
        if macd[-1] > signal[-1] and macd[-2] < signal[-2]:
            # 满仓入股
            ret_code, acc_info = self.trade_ctx.accinfo_query(
                trd_env=self.trade_env)
            if ret_code != 0:
                raise Exception('账户信息获取失败! 请重试: {}'.format(acc_info))

            ret_code, snapshot = self.quote_ctx.get_market_snapshot(
                [self.stock])
            if ret_code != 0:
                raise Exception('市场快照数据获取异常 {}'.format(snapshot))
            lot_size = snapshot['lot_size'][0]
            cur_price = snapshot['last_price'][0]
            cash = acc_info['Power'][0]  # 购买力
            qty = int(math.floor(cash / cur_price))
            qty = qty // lot_size * lot_size

            ret_code, ret_data = self.trade_ctx.place_order(
                price=cur_price,
                qty=qty,
                code=self.stock,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=self.trade_env)
            if not ret_code:
                print(
                    'stop_loss MAKE BUY ORDER\n\tcode = {} price = {} quantity = {}'
                    .format(self.stock, cur_price, qty))
            else:
                print('stop_loss: MAKE BUY ORDER FAILURE: {}'.format(ret_data))

class MACD(object):
    """
    A simple MACD strategy
    """
    # API parameter setting
    api_svr_ip = '127.0.0.1'  # 账户登录的牛牛客户端PC的IP, 本机默认为127.0.0.1
    api_svr_port = 11111  # 富途牛牛端口，默认为11111
    unlock_password = "123456"  # 美股和港股交易解锁密码
    trade_env = TrdEnv.SIMULATE

    def __init__(self, stock, short_period, long_period, smooth_period,
                 observation):
        """
        Constructor
        """
        self.stock = stock
        self.short_period = short_period
        self.long_period = long_period
        self.smooth_period = smooth_period
        self.observation = observation
        self.quote_ctx, self.trade_ctx = self.context_setting()

    def close(self):
        self.quote_ctx.close()
        self.trade_ctx.close()

    def context_setting(self):
        """
        API trading and quote context setting
        :returns: trade context, quote context
        """
        if self.unlock_password == "":
            raise Exception("请先配置交易解锁密码! password: {}".format(
                self.unlock_password))

        quote_ctx = OpenQuoteContext(
            host=self.api_svr_ip, port=self.api_svr_port)

        if 'HK.' in self.stock:
            trade_ctx = OpenHKTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        elif 'US.' in self.stock:
            trade_ctx = OpenUSTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        else:
            raise Exception("不支持的stock: {}".format(self.stock))

        if self.trade_env == TrdEnv.REAL:
            ret_code, ret_data = trade_ctx.unlock_trade(
                self.unlock_password)
            if ret_code == RET_OK:
                print('解锁交易成功!')
            else:
                raise Exception("请求交易解锁失败: {}".format(ret_data))
        else:
            print('解锁交易成功!')

        return quote_ctx, trade_ctx

    def handle_data(self):
        """
        handle stock data for trading signal, and make order
        """
        # 读取历史数据，使用sma方式计算均线准确度和数据长度无关，但是在使用ema方式计算均线时建议将历史数据窗口适当放大，结果会更加准确
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=self.observation)
                   ).strftime('%Y-%m-%d')
        end_dt = today.strftime('%Y-%m-%d')
        ret_code, prices, page_req_key = self.quote_ctx.request_history_kline(self.stock, start=pre_day, end=end_dt)
        if ret_code != RET_OK:
            print("request_history_kline fail: {}".format(prices))
            return

        # 用talib计算MACD取值，得到三个时间序列数组，分别为 macd, signal 和 hist
        # macd 是长短均线的差值，signal 是 macd 的均线
        # 使用 macd 策略有几种不同的方法，我们这里采用 macd 线突破 signal 线的判断方法
        macd, signal, hist = talib.MACD(prices['close'].values,
                                        self.short_period, self.long_period,
                                        self.smooth_period)

        # 如果macd从上往下跌破macd_signal
        if macd[-1] < signal[-1] and macd[-2] > signal[-2]:
            # 计算现在portfolio中股票的仓位
            ret_code, data = self.trade_ctx.position_list_query(
                trd_env=self.trade_env)

            if ret_code != RET_OK:
                raise Exception('账户信息获取失败: {}'.format(data))
            pos_info = data.set_index('code')

            cur_pos = int(pos_info['qty'][self.stock])
            # 进行清仓
            if cur_pos > 0:
                ret_code, data = self.quote_ctx.get_market_snapshot(
                    [self.stock])
                if ret_code != 0:
                    raise Exception('市场快照数据获取异常 {}'.format(data))
                cur_price = data['last_price'][0]
                ret_code, ret_data = self.trade_ctx.place_order(
                    price=cur_price,
                    qty=cur_pos,
                    code=self.stock,
                    trd_side=TrdSide.SELL,
                    order_type=OrderType.NORMAL,
                    trd_env=self.trade_env)
                if ret_code == RET_OK:
                    print('stop_loss MAKE SELL ORDER\n\tcode = {} price = {} quantity = {}'
                          .format(self.stock, cur_price, cur_pos))
                else:
                    print('stop_loss: MAKE SELL ORDER FAILURE: {}'.format(ret_data))

        # 如果短均线从下往上突破长均线，为入场信号
        if macd[-1] > signal[-1] and macd[-2] < signal[-2]:
            # 满仓入股
            ret_code, acc_info = self.trade_ctx.accinfo_query(
                trd_env=self.trade_env)
            if ret_code != 0:
                raise Exception('账户信息获取失败! 请重试: {}'.format(acc_info))

            ret_code, snapshot = self.quote_ctx.get_market_snapshot(
                [self.stock])
            if ret_code != 0:
                raise Exception('市场快照数据获取异常 {}'.format(snapshot))
            lot_size = snapshot['lot_size'][0]
            cur_price = snapshot['last_price'][0]
            cash = acc_info['Power'][0]  # 购买力
            qty = int(math.floor(cash / cur_price))
            qty = qty // lot_size * lot_size

            ret_code, ret_data = self.trade_ctx.place_order(
                price=cur_price,
                qty=qty,
                code=self.stock,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=self.trade_env)
            if not ret_code:
                print(
                    'stop_loss MAKE BUY ORDER\n\tcode = {} price = {} quantity = {}'
                    .format(self.stock, cur_price, qty))
            else:
                print('stop_loss: MAKE BUY ORDER FAILURE: {}'.format(ret_data))
def quote_test():
    '''
    行情接口调用测试
    :return:
    '''
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    # 设置异步回调接口
    quote_ctx.set_handler(StockQuoteTest())
    quote_ctx.set_handler(CurKlineTest())
    quote_ctx.set_handler(RTDataTest())
    quote_ctx.set_handler(TickerTest())
    quote_ctx.set_handler(OrderBookTest())
    quote_ctx.set_handler(BrokerTest())
    quote_ctx.set_handler(SysNotifyTest())
    quote_ctx.start()

    
    stock_type = [SecurityType.STOCK, SecurityType.IDX, SecurityType.ETF, SecurityType.WARRANT,
                  SecurityType.BOND]
    stock_codes = []

    market = Market.US
    stock_codes_watching_list = ['US.PDD', 'US.GSX', 'US.BILI', 'US.DAO', 'US.RCL', 'US.CCL', 'US.BA', 'US.LK']

#     for sub_type in stock_type:
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(market, SecurityType.STOCK, stock_codes_watching_list)
    if ret_code == 0:
#         print("get_stock_basicinfo: market={}, sub_type={}, count={}".format(market, sub_type, len(ret_data)))
        print ret_data
        for ix, row in ret_data.iterrows():
            stock_codes.append(row['code'])

    if len(stock_codes) == 0:
        quote_ctx.close()
        print("Error market:'{}' can not get stock info".format(market))
        return

    print stock_codes[0:5]



    #k line
    today = datetime.datetime.today()
    pre_day = (today - datetime.timedelta(days=self.observation)
               ).strftime('%Y-%m-%d')
    end_dt = today.strftime('%Y-%m-%d')
    ret_code, prices, page_req_key = self.quote_ctx.request_history_kline(self.stock, start=pre_day, end=end_dt)
    if ret_code != RET_OK:
        print("request_history_kline fail: {}".format(prices))
        return


    



    #snap_shot
    ret_code, ret_data = quote_ctx.get_market_snapshot(stock_codes_watching_list[0:0])
    if ret_code != 0:
        print(ret_data)
        sleep(3)


    """
    for i in range(1, min(6, len(stock_codes)), 200):
        print("from {}, total {}".format(i, len(stock_codes)))
        ret_code, ret_data = quote_ctx.get_market_snapshot(stock_codes[i:i + 5])
        if ret_code != 0:
            print(ret_data)
        time.sleep(3)
        """

    quote_ctx.close()
    return 

    # 获取推送数据
#     big_sub_codes = ['HK.02318', 'HK.02828', 'HK.00939', 'HK.01093', 'HK.01299', 'HK.00175',
#                      'HK.00700', 'HK.01177',  'HK.02601', 'HK.02628', 'HK_FUTURE.999010']
#     subtype_list = [SubType.QUOTE, SubType.ORDER_BOOK, SubType.TICKER, SubType.K_DAY, SubType.RT_DATA, SubType.BROKER]

#     sub_codes =  ['HK.00700', 'HK_FUTURE.999010']

#     print("* subscribe : {}\n".format(quote_ctx.subscribe(sub_codes, subtype_list)))

#     sleep(6)
#     sleep(60*60*24)

class MACD(object):
    """
    A simple MACD strategy
    """
    # API parameter setting
    api_svr_ip = '127.0.0.1'  # 账户登录的牛牛客户端PC的IP, 本机默认为127.0.0.1
    api_svr_port = 11111  # 富途牛牛端口，默认为11111
    unlock_password = "123456"  # 美股和港股交易解锁密码
    trade_env = TrdEnv.SIMULATE

    def __init__(self, stock, short_period, long_period, smooth_period,
                 observation):
        """
        Constructor
        """
        self.stock = stock
        self.short_period = short_period
        self.long_period = long_period
        self.smooth_period = smooth_period
        self.observation = observation
        self.quote_ctx, self.trade_ctx = self.context_setting()

    def close(self):
        self.quote_ctx.close()
        self.trade_ctx.close()

    def context_setting(self):
        """
        API trading and quote context setting
        :returns: trade context, quote context
        """
        if self.unlock_password == "":
            raise Exception("请先配置交易解锁密码! password: {}".format(
                self.unlock_password))

        quote_ctx = OpenQuoteContext(
            host=self.api_svr_ip, port=self.api_svr_port)

        if 'HK.' in self.stock:
            trade_ctx = OpenHKTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        elif 'US.' in self.stock:
            trade_ctx = OpenUSTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        else:
            raise Exception("不支持的stock: {}".format(self.stock))

        if self.trade_env == TrdEnv.REAL:
            ret_code, ret_data = trade_ctx.unlock_trade(
                self.unlock_password)
            if ret_code == RET_OK:
                print('解锁交易成功!')
            else:
                raise Exception("请求交易解锁失败: {}".format(ret_data))
        else:
            print('解锁交易成功!????')

        return quote_ctx, trade_ctx

    def handle_data(self):
        """
        handle stock data for trading signal, and make order
        """
        # 读取历史数据，使用sma方式计算均线准确度和数据长度无关，但是在使用ema方式计算均线时建议将历史数据窗口适当放大，结果会更加准确
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=self.observation)
                   ).strftime('%Y-%m-%d')
        end_dt = today.strftime('%Y-%m-%d')
        ret_code, prices, page_req_key = self.quote_ctx.request_history_kline(self.stock, start=pre_day, end=end_dt)
        if ret_code != RET_OK:
            print("request_history_kline fail: {}".format(prices))
            return

#         print self.stock, prices, page_req_key
#         return

        # 用talib计算MACD取值，得到三个时间序列数组，分别为 macd, signal 和 hist
        # macd 是长短均线的差值，signal 是 macd 的均线
        # 使用 macd 策略有几种不同的方法，我们这里采用 macd 线突破 signal 线的判断方法
        macd, signal, hist = talib.MACD(prices['close'].values,
                                        self.short_period, self.long_period,
                                        self.smooth_period)

        print prices
        print macd
        print signal
        return
        # 如果macd从上往下跌破macd_signal
        if macd[-1] < signal[-1] and macd[-2] > signal[-2]:
            # 计算现在portfolio中股票的仓位
            ret_code, data = self.trade_ctx.position_list_query(
                trd_env=self.trade_env)

            if ret_code != RET_OK:
                raise Exception('账户信息获取失败: {}'.format(data))
            pos_info = data.set_index('code')

            cur_pos = int(pos_info['qty'][self.stock])
            # 进行清仓
            if cur_pos > 0:
                ret_code, data = self.quote_ctx.get_market_snapshot(
                    [self.stock])
                if ret_code != 0:
                    raise Exception('市场快照数据获取异常 {}'.format(data))
                cur_price = data['last_price'][0]
                ret_code, ret_data = self.trade_ctx.place_order(
                    price=cur_price,
                    qty=cur_pos,
                    code=self.stock,
                    trd_side=TrdSide.SELL,
                    order_type=OrderType.NORMAL,
                    trd_env=self.trade_env)
                if ret_code == RET_OK:
                    print('stop_loss MAKE SELL ORDER\n\tcode = {} price = {} quantity = {}'
                          .format(self.stock, cur_price, cur_pos))
                else:
                    print('stop_loss: MAKE SELL ORDER FAILURE: {}'.format(ret_data))

        # 如果短均线从下往上突破长均线，为入场信号
        if macd[-1] > signal[-1] and macd[-2] < signal[-2]:
            # 满仓入股
            ret_code, acc_info = self.trade_ctx.accinfo_query(
                trd_env=self.trade_env)
            if ret_code != 0:
                raise Exception('账户信息获取失败! 请重试: {}'.format(acc_info))

            ret_code, snapshot = self.quote_ctx.get_market_snapshot(
                [self.stock])
            if ret_code != 0:
                raise Exception('市场快照数据获取异常 {}'.format(snapshot))
            lot_size = snapshot['lot_size'][0]
            cur_price = snapshot['last_price'][0]
            cash = acc_info['Power'][0]  # 购买力
            qty = int(math.floor(cash / cur_price))
            qty = qty // lot_size * lot_size

            ret_code, ret_data = self.trade_ctx.place_order(
                price=cur_price,
                qty=qty,
                code=self.stock,
                trd_side=TrdSide.BUY,
                order_type=OrderType.NORMAL,
                trd_env=self.trade_env)
            if not ret_code:
                print(
                    'stop_loss MAKE BUY ORDER\n\tcode = {} price = {} quantity = {}'
                    .format(self.stock, cur_price, qty))
            else:
                print('stop_loss: MAKE BUY ORDER FAILURE: {}'.format(ret_data))



def macd(stock):
    SHORT_PERIOD = 12
    LONG_PERIOD = 26
    SMOOTH_PERIOD = 9
    OBSERVATION = 100

    test = MACD(stock, SHORT_PERIOD, LONG_PERIOD, SMOOTH_PERIOD, OBSERVATION)
    test.handle_data()
    test.close()


def subscribe_test():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    quote_ctx.subscribe(['HK.00763'], [SubType.QUOTE])
    ret, data = quote_ctx.query_subscription()
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
    quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽


def rt_test():
    quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
    ret_sub, err_message = quote_ctx.subscribe(['HK.00763'], [SubType.TICKER], subscribe_push=False)

    if ret_sub == RET_OK:  # 订阅成功
        ret, data = quote_ctx.get_rt_ticker('HK.00763', 9)  # 获取港股00700最近2个逐笔
        if ret == RET_OK:
            print(data)
            print(data['turnover'][0])   # 取第一条的成交金额
            print(data['turnover'].values.tolist())   # 转为list
        else:
            print('error:', data)
    else:
        print('subscription failed', err_message)
    quote_ctx.close()  # 关闭当条连接，OpenD会在1分钟后自动取消相应股票相应类型的订阅

def rt_test2():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_sub, err_message = quote_ctx.subscribe(['HK.00700'], [SubType.RT_DATA], subscribe_push=False)
    # 先订阅分时数据类型。订阅成功后OpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
    if ret_sub == RET_OK:   # 订阅成功
        ret, data = quote_ctx.get_rt_data('HK.00700')   # 获取一次分时数据
        if ret == RET_OK:
            print(data)
        else:
            print('error:', data)
    else:
        print('subscription failed', err_message)
    quote_ctx.close()   # 关闭当条连接，OpenD会在1分钟后自动取消相应股票相应类型的订阅



def order_book_test():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_sub = quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK], subscribe_push=False)[0]
    # 先订阅买卖摆盘类型。订阅成功后 OpenD 将持续收到服务器的推送，False 代表暂时不需要推送给脚本
    if ret_sub == RET_OK:  # 订阅成功
        ret, data = quote_ctx.get_order_book('HK.00700', num=3)  # 获取一次 3 档实时摆盘数据
        if ret == RET_OK:
            print(data)
        else:
            print('error:', data)
    else:
        print('subscription failed')
    quote_ctx.close()  # 关闭当条连接，OpenD 会在 1 分钟后自动取消相应股票相应类型的订阅


def security_test():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    ret, data = quote_ctx.get_user_security("HK")
    if ret == RET_OK:
        print(data)
        print(data['code'][0])    # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为list
    else:
        print('error:', data)
    quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽
    
if __name__ =="__main__":
    set_futu_debug_model(True)
    '''
    默认rsa密钥在futu.common下的conn_key.txt
    注意同步配置FutuOpenD的FTGateway.xml中的 rsa_private_key 字段
    '''
    # SysConfig.set_init_rsa_file()

    ''' 是否启用协议加密 '''
    # SysConfig.enable_proto_encrypt(False)

    '''设置通讯协议格式 '''
    # SysConfig.set_proto_fmt(ProtoFMT.Json)

    '''设置client信息'''
    # SysConfig.set_client_info('sample', 0)

    ''' 行情api测试 '''
#     quote_test()

    ''' 交易api测试 '''
    # trade_hk_test()

    # trade_hkcc_test()
    rt_test2()
    #subscribe_test()
    #order_book_test()
    
    #fail
    #security_test()
    
    #stock_codes_watching_list = ['HK.09999', 'HK.00763']
    #for code in stock_codes_watching_list:
    #    macd(code)

