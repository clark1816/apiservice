import os, csv
from pandas.core.frame import DataFrame
import yfinance as yf
import pandas as pd
from flask import Flask, render_template, request
from patterns import patterns
import talib

# from fastapi import FastAPI, Request
# from fastapi.templating import Jinja2Templates

# app2 = FastAPI()

# templates = Jinja2Templates(directory="E:/programmin/NewScreenerApp/templates")

app = Flask(__name__)

# @app2.get("/tradingview_widget")
# async def tradingview_widget(request: Request):
#     return templates.TemplateResponse("tradingview.html", {"request": request})

@app.route("/")
def index():
    pattern  = request.args.get('pattern', None)
    stocks = {}

    with open('dataset/compaines.csv') as f:
        for row in csv.reader(f):
            stocks[row[0]] = {'company': row[1]}
    print(stocks)
    if pattern:
        datafiles = os.listdir('dataset/daily')
        for filename in datafiles:
            df=pd.read_csv('dataset/daily/{}'.format(filename))
            
            pattern_function = getattr(talib, pattern)

            symbol = filename.split('.')[0]

            try:
                result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]
                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol] [pattern] = 'bearish'
                else:
                     stocks[symbol] [pattern] = None
            except:
                pass

    return render_template('index.html', patterns=patterns, stocks = stocks, current_pattern=pattern)

@app.route('/snapshot')
def snapshot():
    with open('dataset/compaines.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = (company.split(',')[0])
            df = yf.download(symbol, start="2021-09-01", end="2021-11-1")
            df.to_csv('dataset/daily/{}.csv'.format(symbol))
    return{
        'code': 'success'
    }

if __name__ == "__main__":
    port = os.environ.get("PORT", 5000) #Heroku will set PORT enviroment
    app.run(debug=False, host="0.0.0.0", port=port)