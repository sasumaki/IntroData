# Python modules
import geopandas as gpd
import pandas as pd
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Point
import ctypes
from descartes import PolygonPatch
import math
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt
from scipy.cluster.vq import kmeans2
import numpy as np



# Own modules
import readFiles
import geopandas_osm.osm as osm


def main():
	data=readFiles.readFiles()
	
	plt.plot(data.xkoord, data.ykoord, '.', alpha=0.05)
	plt.show()


def wrangleData(df):
	values_to_remove = ["FID","grd_id","gid"]

	for val in values_to_remove:
		del df[val]
    
	return df


#Plot the metropolitan area colormapped by population and background map with postal-areas
#EPSG:3067: ETRS89 / ETRS-TM35FIN / EUREF-FIN
#Areacodes: Helsinki = 91, Espoo = 49, Vantaa = 92, Kauniainen = 235

def plotMetropolitan(scatterMap):
	df = readFiles.readFiles()
	df = wrangleData(df)
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]
   
	df_road = gpd.read_file("metropolitan/metropolitan_helsinki_roads_gen1.geojson")
	df_road = df_road.to_crs(epsg=3067)
	df_admin = gpd.read_file("metropolitan/metropolitan_helsinki_admin.geojson")
	df_admin = df_admin.to_crs(epsg=3067)
	
	fig, ax = plt.subplots()

	df_road.plot(ax=ax, color="rebeccapurple", alpha=1,linewidth=0.5, zorder=0)
	boundaries = list()
	pops = list()
	for i in xrange(0,len(df_admin)):
		#adminlevel = df_admin.ix[i].admin_leve
		#if  adminlevel < 10:
			boundary = df_admin.ix[i].geometry
			totalpop = 0
			squares = 1
			for  kunta, id_nro, vaesto, miehet, naiset, ika1,ika2,ika3,x,y,point in df.values:
				point = Point(x,y)
				if boundary.contains(point):
					totalpop = totalpop + vaesto
					squares = squares + 1
								
			boundaries.append(boundary)
			totalpop = totalpop/squares
			pops.append(totalpop)
	
	jet = cm = plt.get_cmap('Wistia') 
	cNorm  = colors.Normalize(vmin=min(pops), vmax=max(pops))
	scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
	idx = 0
	for boundary in boundaries:
		if not isinstance(boundary, Polygon):
			continue
		if scatterMap == True:
			col = "grey"
		else:
			col = scalarMap.to_rgba(pops[idx])
		patch = PolygonPatch(boundary,gid=idx, alpha=0.75, zorder=-1, fc=col)
		ax.add_patch(patch)
		idx = idx + 1 
		

	df_hsl = gpd.read_file("HSL_stopsbyroutes/HSLn_pysakit_linjoittain.shp")

	df_hsl = df_hsl.to_crs({'init': 'epsg:3067'})
	df_hsl["xkoord"] = df_hsl["geometry"].x
	df_hsl["ykoord"] = df_hsl["geometry"].y
	

	

	def kmeansInput(input0, weightVar):
         output0=np.array(input0[['xkoord', 'ykoord', weightVar]])
    	 output0=np.repeat(output0, output0[:,2], axis=0)
    	 output0=output0[:,:2] * 1.0
    	 return output0
	#weight vars: 'vaesto', 'miehet', 'naiset','ika_0_14', 'ika_15_64', 'ika_65_'
	weightedData=kmeansInput(df, 'vaesto')
	weightedHSL = np.array(df_hsl[["xkoord", "ykoord"]])
	weightedHSL = np.repeat(weightedHSL, 50,axis=0)
	
	weightedHSL = weightedHSL[:,:2]* 1.0

	

	weightedData = np.concatenate((weightedData, weightedHSL))

	result = kmeans2(weightedData,5)
	tulos=np.array(result[0])
	plt.plot(tulos[:,0], tulos[:,1], 'o', markersize=15,markerfacecolor='red')

	if(scatterMap == True):
		scattermap(df)

	ax.set_facecolor("silver")
	ax.axes.get_xaxis().set_visible(False)
	ax.axes.get_yaxis().set_visible(False)
	def on_plot_hover(event):
         for curve in plot.get_lines():
        	if curve.contains(event)[0]:
            	 print "over %s" % curve.get_gid()

	#plt.ion()
	#fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)  
	plt.show()
	plt.savefig("temp.png")

def scattermap(df):
		cm = plt.cm.get_cmap('Wistia')
		df["vaestolog"] = df["vaesto"]
		df["vaestolog"] = df["vaestolog"].apply(lambda x: math.log(x))

		padding = df["vaestolog"].mean()/2
		vmin = df["vaesto"].argmin()
		vmax = df["vaesto"].argmax()

		plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=25, alpha=1, cmap = cm,vmin = vmin, vmax = vmax, zorder=1)


print("execute main")
plotMetropolitan(False)
print("done")