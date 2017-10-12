# Python modules
import matplotlib.pyplot as plt
import geopandas as gpd
import geopandas_osm.osm as osm
from shapely.geometry.polygon import LinearRing, Polygon



# Own modules
import readFiles

def main():
	data=readFiles.readFiles()
	plt.plot(data.xkoord, data.ykoord, '.', alpha=0.05)
	plt.show()


#Plot the metropolitan area colormapped by population and background map with postal-areas
#EPSG:3067: ETRS89 / ETRS-TM35FIN / EUREF-FIN

def plotMetropolitan():
	df=readFiles.readFiles()
	#codes: Helsinki = 91, Espoo = 49, Vantaa = 92, Kauniainen = 235
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]

	df_road = gpd.read_file("metropolitan/metropolitan_finland_roads_gen1.geojson")

	df_road = df_road.to_crs(epsg=3067)
	df_admin = gpd.read_file("metropolitan/metropolitan_finland_admin.geojson")
	df_admin = df_admin.to_crs(epsg=3067)


	ax = df_road.plot(color="blue", alpha=1,linewidth=0.5, zorder=-1)

	for i in xrange(0,len(df_admin)):
		boundary = df_admin.ix[i].geometry
		x,y = boundary.exterior.xy
		ax.plot(x,y,color="black",linewidth=0.8,zorder=0)

	

	#This is for creating a colormap of the populations
	cm = plt.cm.get_cmap('YlOrRd')
	vmin = df["vaesto"].argmin()
	vmax = (df["vaesto"].argmax()-df["vaesto"].mean())/2

	plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=20, alpha=1, cmap = cm,vmin = vmin, vmax = vmax, zorder=1)	
	ax.set_axis_bgcolor("lightgray")
	plt.show()


print("execute main")
plotMetropolitan()
print("done")