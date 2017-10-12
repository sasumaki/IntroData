# Python modules
import matplotlib.pyplot as plt
import geopandas as gpd

# Own modules
import readFiles

def main():
	data=readFiles.readFiles()
	plt.plot(data.xkoord, data.ykoord, '.', alpha=0.05)
	plt.show()


#Plot the metropolitan area colormapped by population and background map with postal-areas
def plotMetropolitan():
	df=readFiles.readFiles()
	#codes: Helsinki = 91, Espoo = 49, Vantaa = 92, Kauniainen = 235
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]

	metropolitan = gpd.read_file('Postinumeroalueet_2015_shp/Postinumeroalueet_2015_shp.shp')
	metropolitan = metropolitan.to_crs(epsg=3067) #EPSG:3067:  ETRS89 / ETRS-TM35FIN / EUREF-FIN

	metropolitan.plot(color = "grey")
	
	#This is for creating a colormap of the populations
	cm = plt.cm.get_cmap('Wistia')
	vmin = df["vaesto"].argmin()
	vmax = df["vaesto"].argmax()

	plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=8, cmap = cm,vmin = vmin, vmax = vmax, alpha=.8)	
	plt.show()


print("execute main")
plotMetropolitan()
print("done")