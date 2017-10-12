# Python modules
import matplotlib.pyplot as plt
import geopandas as gpd
import geopandas_osm.osm as osm




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

	#df_building = gpd.read_file("metropolitan/metropolitan_finland_buildings.geojson")
	df_road = gpd.read_file("metropolitan/metropolitan_finland_roads_gen1.geojson")

	#df_building = df_building.to_crs(epsg=3067)
	df_road = df_road.to_crs(epsg=3067)
	

	#df_building.plot(color="blue", alpha=.7)
	ax = df_road.plot(color="black", alpha=1)

	#This is for creating a colormap of the populations
	cm = plt.cm.get_cmap('Wistia')
	vmin = df["vaesto"].argmin()
	vmax = (df["vaesto"].argmax()-df["vaesto"].mean())/2

	plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=25, cmap = cm,vmin = vmin, vmax = vmax)	
	ax.set_axis_bgcolor("gray")
	plt.show()


print("execute main")
plotMetropolitan()
print("done")