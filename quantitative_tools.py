import mplfinance as mpf
import pandas as pd
import talib as ta

class key:
    tiingo = 'ENTER_tiingo_KEY'

# 畫 cnadle 圖
def candle_chart(df, n=0):
    # 抓取近 n 日的資料
    df_resize = df.iloc[n*-1:,:]

    # 繪製K線圖
    mpf.plot(df_resize, type='candle')
    return

class Signal:
    # Evening_Star
    # 第1根是陽線，第2根可以是陽線或陰線，第3根是陰線。
    # 第2根的開盤價與收盤價(也就是灰色方塊的部分)都要大於第1根的收盤價與第3根的開盤價。
    # 第3根的方塊長度要大於第1根的方塊長度的一半。
    def CDLEVENINGSTAR(df):
        return ta.CDLEVENINGSTAR(df.Open.values,df.High.values,df.Low.values,df.Close.values)

    # RSI = 100 × 前N日漲幅的平均值 ÷ ( 前N日漲幅的平均值 + 前N日跌幅的平均值 )  [0~100]
    # RSI相對低點買入(20)，相對高點賣出(80)
    def RSI(df, period=14, upper=80, lower=20):
        # RSI
        RSI = index.RSI(df.Close, period)
        # 訊號標籤
        sig = []
        # 庫存標籤，只會是0或1，表示每次交易都是買進或賣出所有部位
        stock = 0
        # 偵測RSI訊號
        for i in range(len(RSI)):
            if RSI[i] > upper and stock == 1:
                stock -= 1
                sig.append(-1)
            elif RSI[i] < lower and stock == 0:
                stock += 1
                sig.append(1)
            else:
                sig.append(0)
        # 將格式轉成 time series
        rsi_sig = pd.Series(index = RSI.index, data = sig)
        return rsi_sig

class index:
    def SMA(df, timeperiod=5):
        return ta.SMA(df.Close, timeperiod)
        
    def RSI(Close, period=14):
        # 整理資料
        import pandas as pd
        Chg = Close - Close.shift(1)
        Chg_pos = pd.Series(index=Chg.index, data=Chg[Chg>0])
        Chg_pos = Chg_pos.fillna(0)
        Chg_neg = pd.Series(index=Chg.index, data=-Chg[Chg<0])
        Chg_neg = Chg_neg.fillna(0)
        
        # 計算12日平均漲跌幅度
        import numpy as np
        up_mean = []
        down_mean = []
        for i in range(period+1, len(Chg_pos)+1):
            up_mean.append(np.mean(Chg_pos.values[i-period:i]))
            down_mean.append(np.mean(Chg_neg.values[i-period:i]))
        
        # 計算 RSI
        rsi = []
        for i in range(len(up_mean)):
            rsi.append( 100 * up_mean[i] / ( up_mean[i] + down_mean[i] ) )
        rsi_series = pd.Series(index = Close.index[period:], data = rsi)
        return rsi_series

# 回測交易
def backtest(signal, price,offset:int=0):
    # 每次買賣的報酬率
    rets = []
    # 是否仍有庫存
    stock = 0
    # 當次交易買入價格
    buy_price = 0
    # 當次交易賣出價格
    sell_price = 0
    # 每次買賣的報酬率
    for i in range(len(signal)-1):
        if signal[i] == 1:
            # 買入
            buy_price = price[signal.index[i+offset]]
            stock += 1
        elif signal[i] == -1:
            # 賣出
            sell_price = price[signal.index[i+offset]]
            stock -= 1
            rets.append((sell_price-buy_price)/buy_price)
            buy_price = 0
            sell_price = 0
    # 如果最後手上有庫存，就用回測區間最後一天的價賣掉
    if stock == 1 and buy_price != 0 and sell_price == 0:
        sell_price = signal[-1]
        rets.append((sell_price-buy_price)/buy_price)
    # 總報酬率
    total_ret = 1
    for ret in rets:
        total_ret *= 1 + ret
    return total_ret
        


class tiingo:
    # tiingo 資料畫 K 線圖
    def candle_chart(df, n=0):
        df_adj = tiingo.candle_adj(df)

        candle_chart(df_adj, n)
        return 
    
    # 畫 K 線圖前的調整
    def candle_adj(df):
         # 將multi-index轉成single-index
        df = df.reset_index(level=[0,1])

        # 指定date為index
        df.index = df['date']

        # 取adjClose至adjOpen的欄位資料  /adjClose~adjOpen/
        df_adj = df.iloc[:,7:11]

        # 更改columns的名稱，以讓mplfinance看得懂
        df_adj.columns = ['Close','High','Low','Open']

        return df_adj
