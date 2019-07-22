import sys, os.path, csv, plotly, scipy.stats
import plotly.graph_objs as go

stats_file = "result.csv"
tools = ["base","nullaway","eradicate","checkerframework"]
colors = ['#7f7f7f','#2ca02c','#1f77b4','#ff7f0e']

def make_series(records, key, keyi=1, xi=0, yi=2):
	series_recs = list(filter(lambda r: r[keyi]==key, records))
	return None if not series_recs else go.Bar(
		x=[rec[xi] for rec in series_recs],
		y=[float(rec[yi]) for rec in series_recs],
		marker = dict(color = colors[tools.index(key)]),
		name=key
	)

def normalize(data, series, base=0):
	data[series].y = [data[series].y[data[series].x.index(basex)]/ data[base].y[i] if basex in data[series].x and data[base].y[i]>0 else 0 for i, basex in enumerate(data[base].x)]

def mean(data, series):
	data[series].x = data[series].x + ("MEAN",)
	data[series].y = data[series].y + (scipy.stats.gmean(data[series].y),)

norm = False
if len(sys.argv) > 1:
	for arg in sys.argv[1:]:
		if arg in ["-n","-normalize"]:
			norm = True
			sys.argv.remove(arg)
if len(sys.argv) > 1:
	stats_file = sys.argv[1]
if os.path.exists(stats_file): stats_file = os.path.abspath(stats_file)
else: exit("Error: Stats file not found!")

with open(stats_file) as file: records = [rec for rec in csv.reader(file)]
data = list(filter(None, [make_series(records, tool) for tool in tools]))
if norm:
	for i in reversed(range(len(data))):
		normalize(data, i)
		mean(data, i)
fig = go.Figure(data=data, layout=go.Layout(barmode='group',title=('Normalized ' if norm else '')+'Build Times'))
plotly.offline.plot(fig, filename=stats_file.replace('.csv',('_norm' if norm else '_abs')+'.html'))
