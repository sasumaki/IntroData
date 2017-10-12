# Python modules
import matplotlib.pyplot as plt
import geopandas as gpd
import geopandas_osm as osm




# Own modules
import readFiles

def main():
	data=readFiles.readFiles()
	plt.plot(data.xkoord, data.ykoord, '.', alpha=0.05)
	plt.show()


#Plot the metropolitan area colormapped by population and background map with postal-areas
#EPSG:3067: ETRS89 / ETRS-TM35FIN

def plotMetropolitan():
	df=readFiles.readFiles()
	#codes: Helsinki = 91, Espoo = 49, Vantaa = 92, Kauniainen = 235
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]

	df_map = gpd.read_file("helsinki_finland/helsinki_finland_roads.geojson")

	admin_df = gpd.read_file('helsinki_finland/helsinki_finland_admin.geojson')
	print(admin_df[admin_df["admin_leve" == 8.0]])
	sg_boundary = admin_df[admin_df["admin_leve" == 8.0]].geometry
	
	df_map = geopandas_osm.osm.query_osm('way', sg_boundary, recurse='down', tags='highway')

	df_map = df_map.to_crs(epsg=3067)
	df_map.plot()

	#This is for creating a colormap of the populations
	cm = plt.cm.get_cmap('Wistia')
	vmin = df["vaesto"].argmin()
	vmax = df["vaesto"].argmax()

	plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=8, cmap = cm,vmin = vmin, vmax = vmax, alpha=.8)	
	plt.show()


print("execute main")
plotMetropolitan()
print("done")