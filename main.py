# Python modules
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry.polygon import LinearRing, Polygon
from shapely.geometry import Point
import ctypes
from descartes import PolygonPatch
import math



# Own modules
import readFiles
import geopandas_osm.osm as osm
import Color


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

def plotMetropolitan():
	df=readFiles.readFiles()
	df = wrangleData(df)
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]

	df_road = gpd.read_file("metropolitan/metropolitan_helsinki_roads_gen1.geojson")
	df_road = df_road.to_crs(epsg=3067)
	df_admin = gpd.read_file("metropolitan/metropolitan_helsinki_admin.geojson")
	df_admin = df_admin.to_crs(epsg=3067)


	ax = df_road.plot(color="rebeccapurple", alpha=1,linewidth=0.5, zorder=0)
	boundaries = list()
	pops = list()
	for i in xrange(0,len(df_admin)):
		adminlevel = df_admin.ix[i].admin_leve
		if  adminlevel <= 9 or adminlevel == 11:
			boundary = df_admin.ix[i].geometry
			totalpop = 0
			for  kunta, id_nro, vaesto, miehet, naiset, ika1,ika2,ika3,x,y,point in df.values:
				point = Point(x,y)
				if boundary.contains(point):
					totalpop = totalpop + vaesto
								
			boundaries.append(boundary)
			pops.append(totalpop)
	minpop = min(pops)
	maxpop = max(pops)
	
	print(pops)
	for pop in pops:
		pop = (pop-minpop)/(maxpop-minpop)
	print(pops)	
	patch = PolygonPatch(boundary, alpha=0.5, zorder=-1, fc=col)
	ax.add_patch(patch)
		
	#This is for creating a colormap of the populations
	cm = plt.cm.get_cmap('Wistia')
	df["vaestolog"] = df["vaesto"]
	df["vaestolog"] = df["vaestolog"].apply(lambda x: math.log(x))

	padding = df["vaestolog"].mean()/2
	vmin = df["vaesto"].argmin()
	vmax = df["vaesto"].argmax()

	plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=25, alpha=1, cmap = cm,vmin = vmin, vmax = vmax, zorder=1)	
	ax.set_facecolor("silver")
	plt.show()


print("execute main")
plotMetropolitan()
print("done")