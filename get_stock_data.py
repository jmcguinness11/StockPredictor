import pandas as pd, numpy as np, datetime

def getStockPrices(company, mins_bw_reports, num_days):
	url = "http://www.google.com/finance/getprices?q={}&i={}&p={}d&f=d,o,h,l,c,v".format(company, 60*mins_bw_reports, num_days)
	x=np.array(pd.read_csv(url,skiprows=7,header=None))
	date=[]
	remove_inds = []
	for i in range(0,len(x)):
		if x[i][0][0]=='a':
			t = datetime.datetime.fromtimestamp(int(x[i][0].replace('a','')))
			x[i][0] = 0
			date.append(t)
		elif x[i][0][0] == 'T':
			remove_inds.append(i)
		else:
			time = t+datetime.timedelta(minutes = int(x[i][0]))
			date.append(time)
	x = np.delete(x, remove_inds, axis=0)
	data1 = pd.DataFrame(x,index=date)
	data1.columns=['a','Open','High','Low','Close','Vol']
	return data1

data = getStockPrices('AAPL', 120, 10)
print data.head()
print data.tail()
