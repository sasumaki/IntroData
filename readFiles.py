
# read files
import pandas as pd

def readFiles(files=""):
	data = pd.read_csv("http://geo.stat.fi/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=vaki2016_1km_kp&outputFormat=csv")
	return data