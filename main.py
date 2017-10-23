# coding=utf-8
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
import copy 
import geopandas_osm.osm



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

def plotMetropolitan(scatterMap, annotate, numberOfK):
	df = readFiles.readFiles()
	df = wrangleData(df)
	df = df[(df["kunta"] == 91) | (df["kunta"] == 49) | (df["kunta"] == 92) | (df["kunta"] == 235)]
   
	df_road = gpd.read_file("metropolitan/metropolitan_helsinki_roads_gen1.geojson")
	df_road = df_road.to_crs(epsg=3067)
	df_admin = gpd.read_file("metropolitan/metropolitan_helsinki_admin.geojson")
	df_admin = df_admin.to_crs(epsg=3067)
	print(df_admin.geometry)
	fig = plt.figure(1)
	ax = fig.add_subplot(1, 1, 1, aspect='equal', adjustable='box-forced')
	
	df_road.plot(ax=ax, color="rebeccapurple", alpha=1,linewidth=0.5, zorder=0)
	boundaries = list()
	pops = list()
	for i in range(0,len(df_admin)):
		adminlevel = df_admin.ix[i].admin_leve
		boundary = df_admin.ix[i].geometry
		centroid = boundary.centroid
		x = centroid.x
		y = centroid.y
		if  adminlevel == 10 and annotate==True:
			ax.annotate(df_admin.ix[i]["name"], xy=(x,y), ha='center')
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

	result = kmeans2(weightedData,numberOfK)
	tulos=np.array(result[0])
	print(tulos)
	plt.plot(tulos[:,0], tulos[:,1], 'o', markersize=10,markerfacecolor='red')
	title = 1
	for point in tulos:
		print(point)
		ax.annotate(title, xy=point, color="white")
		title = title + 1
	

	resultPoints=pd.DataFrame(tulos, columns=['x', 'y'])
	resultPoints['suggestion']=resultPoints.apply(lambda row: Point(row["x"], row["y"]), axis=1)
	crs0 = {'init': 'epsg:3067'}
	resultPoints=gpd.GeoDataFrame(resultPoints, crs=crs0, geometry='suggestion')

	if(scatterMap == True):
		scattermap(df)

	ax.set_facecolor("silver")
	ax.axes.get_xaxis().set_visible(False)
	ax.axes.get_yaxis().set_visible(False)
	def on_plot_hover(event):
		for curve in plot.get_lines():
			if curve.contains(event)[0]:
				print("over %s" % curve.get_gid())

	#plt.ion()
	#fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)  
	findNearestBuildings(resultPoints,fig, numberOfK)
	
	plt.show()
	plt.savefig("temp.png")
def findNearestBuildings(resultPoints, fig, numberOfK):
	# Rakennusdata samaan tiedostoon ja koordinaattisysteemiin
	crs0={'init': 'epsg:3067'}
	rakVan=gpd.read_file("vanRak.json", crs=crs0,encoding="utf-8")
	rakVan = rakVan.rename(columns={rakVan.columns[4]: "kayttotarkoitus_koodi" })

	rakVan = rakVan.rename(columns={"käyttötarkoitus_koodi": "kayttotarkoitus_koodi"})
	rakEsp=gpd.read_file("espRak.json", crs=crs0,encoding="utf-8")
	rakHel=gpd.GeoDataFrame.from_file(r"rakennukset2012/rakennukset_Helsinki_wgs84/rakennukset_Helsinki_06_2012_wgs84.TAB", crs=crs0,encoding="utf-8")
	rakVan=rakVan.to_crs({'init': 'epsg:3067'})
	rakHel=rakHel.to_crs({'init': 'epsg:3067'})
	rakEsp=rakEsp.to_crs({'init': 'epsg:3067'})

# Parsitaan Espoolle ja Vantaalle kirjainkoodit
	kayttoluokitus0=pd.read_table('kayttotarkoitusluokitus.txt', index_col=False, sep='\t', skiprows=1, header=None)
	kayttoluokitus0.columns=['koodi', 'selite']
	kaytto, selite = '', ''
	kayttoluokitus=pd.DataFrame(columns=['koodi', 'selite','koodiPitka','selitePitka', 'koodiPitkaNum'], dtype=str)
	for index, row in kayttoluokitus0.iterrows():
		if row['koodi'].isalpha():
			koodi=row['koodi']
			selite=row['selite']
		else:
			koodiPitka=row['koodi']
			selitePitka=row['selite']
			kayttoluokitus.loc[index, 'koodi']=koodi
			kayttoluokitus.loc[index, 'selite']=selite
			kayttoluokitus.loc[index, 'koodiPitka']=koodiPitka
			kayttoluokitus.loc[index, 'selitePitka']=selitePitka
			kayttoluokitus.loc[index, 'koodiPitkaNum']=int(koodiPitka)
			kayttoluokitus.drop_duplicates('koodiPitkaNum', inplace=True)

	# Espoo
	rakEsp=pd.merge(rakEsp, kayttoluokitus[['koodi', 'koodiPitkaNum']], left_on='kayttotarkoitusnumero', right_on='koodiPitkaNum')
	rakEsp['osoite']=rakEsp.katunimi + ' ' +rakEsp.osoitenumero + ' Espoo'
	rakEsp1=rakEsp[['koodi','osoite','geometry']]
	rakEsp1.columns=['koodi','osoite','building']
	# Vantaa
	rakVan=pd.merge(rakVan, kayttoluokitus[["koodi", "koodiPitka"]], left_on="kayttotarkoitus_koodi", right_on="koodiPitka")
	rakVan['osoite']=rakVan.katuosoite_suomeksi + ' Vantaa'
	rakVan1=rakVan[['koodi', 'osoite', 'geometry']]
	rakVan1.columns=['koodi','osoite','building']
	#  HElsinki
	rakHel1=rakHel[["kayttotark_t1koodi", "Osoite", "geometry"]]
	rakHel1.columns=['koodi', 'osoite', 'building']
	rak=pd.concat((rakEsp1, rakVan1,rakHel1))
	rak=rak.set_geometry('building')
	print("Rakennusten geometriasarake: ", rak.geometry.name)
#rak['geometry2']=rak.centroid
	#Geometrian vaihto, jos tarpeen käyttää rakennusten keskipisteitä
	#rak=rak.set_geometry('geometry2')
	
	#A Asuinrakennukset B Vapaa-ajan asuinrakennukset C Liikerakennukset D Toimistorakennukset
	#E Liikenteen rakennukset F Hoitoalan rakennukset G Kokoontumisrakennukset H Opetusrakennukset
	#J Teollisuusrakennukset K Varastorakennukset L Palo- ja pelastustoimen rakennukset 
	#M Maatalousrakennukset N Muut rakennukset

	rakennusTyyppi='D'
	retVal=placeSuggestions(resultPoints, rak[(rak['koodi']==rakennusTyyppi) | (rak['koodi']=='F') | (rak['koodi']=='C')])
	#rak=rak[['koodi', 'osoite', 'building']]
	#test0=pd.DataFrame(rak)
	#test0['test']=0
	#print(rak.columns)
	#print(test0.columns)	
	# plot 5 nearest locations
	buildingSuggestions=gpd.GeoDataFrame(retVal[['pointIndex','building','osoite']], geometry='building', crs=crs0)
	points=gpd.GeoDataFrame(retVal[['pointIndex','point']], geometry='point', crs=crs0)
	print(retVal.head())
	print(buildingSuggestions.crs)
	print(len(rak))
	i=0
	
	while i <= max(points["pointIndex"]):
		print(buildingSuggestions.geometry, buildingSuggestions.crs)
		fig = plt.figure(i+2)
		buildingPlot = fig.add_subplot(111, aspect='equal', adjustable='box-forced')
		buildingPlot.set_title(i+1)
		buildingsOfIndex = buildingSuggestions[buildingSuggestions["pointIndex"] == i]
		df_road = gpd.read_file("metropolitan/metropolitan_helsinki_roads_gen1.geojson")
		df_road = df_road.to_crs(epsg=3067)
		df_road.plot(ax=buildingPlot, color="rebeccapurple", alpha=1, zorder=0)
		axisX = max(buildingsOfIndex["building"].centroid.x)
		axisX0 = min(buildingsOfIndex["building"].centroid.x)
		axisY = max(buildingsOfIndex["building"].centroid.y)
		axisY0 = min(buildingsOfIndex["building"].centroid.y)
		poly = Polygon([[axisX0,axisY0],[axisX0,axisY],[axisX,axisY],[axisX,axisY0]])
		for building in rak["building"]:
			if poly.contains(building):
				patch = PolygonPatch(building , alpha=0.75, zorder=-1, fc="red")
				buildingPlot.add_patch(patch)
		
		if (axisX - axisX0) < 250:
			paddingX = 250
		else:
			paddingX = (axisX - axisX0)*0.2
		if(axisY-axisY0) < 250:
			paddingY = 250
		else:
			paddingY = (axisY - axisY0)*0.2
			

		buildingPlot.axis([axisX0 - paddingX,axisX+paddingX,axisY0-paddingY,axisY+paddingY])
		buildingPlot.axes.get_xaxis().set_visible(False)
		buildingPlot.axes.get_yaxis().set_visible(False)
		buildingSuggestions[buildingSuggestions["pointIndex"]==i].plot(ax=buildingPlot)
		j = 0
		for j in range(len(buildingSuggestions[buildingSuggestions["pointIndex"]==i])):
			#print(buildingSuggestions[buildingSuggestions["pointIndex"]==i]["osoite"].iloc[j])
			print("aids")
			print(buildingSuggestions[buildingSuggestions["pointIndex"]==i]["building"].iloc[j].centroid.x)
			print(buildingSuggestions[buildingSuggestions["pointIndex"]==i]["building"].iloc[j].centroid.y)

			buildingPlot.annotate(buildingSuggestions[buildingSuggestions["pointIndex"]==i]["osoite"].iloc[j], xy=(buildingSuggestions[buildingSuggestions["pointIndex"]==i]["building"].iloc[j].centroid.x, buildingSuggestions[buildingSuggestions["pointIndex"]==i]["building"].iloc[j].centroid.y))
			j = j + 1 
		
		points[points['pointIndex']==i].plot(ax=buildingPlot)
		i = i + 1
	
	print(buildingSuggestions, points)
#kunnat3.plot(color='white', edgecolor='black')

def placeSuggestions(points, buildings, nSuggestions=3):
    returnFrame=pd.DataFrame()
    for j in range(len(points)):
        print("round starts ", j)
        returnFrame0=pd.DataFrame() 
        point0=gpd.GeoDataFrame([points.iloc[j]], geometry='suggestion')
        #lasketaan rakennuksille etäisyydet
        for i in range(len(buildings)):
            point00=point0['suggestion'].iloc[0]
            px, py=point00.centroid.coords.xy
            building0=buildings['building'].iloc[i]
            bx, by=building0.centroid.coords.xy
            dist=np.sqrt( (px[0]-bx[0])**2 + (py[0]-by[0])**2 )
            returnFrame0=returnFrame0.append(([[j, i, dist, building0, point00,buildings["osoite"].iloc[i]]]))
        returnFrame=returnFrame.append(returnFrame0.nsmallest(nSuggestions, 2))
        print("round ends ", j)
    returnFrame.columns=['pointIndex', 'buildingIndex', 'dist', 'building', 'point', 'osoite']
    return returnFrame

	
def scattermap(df):
		cm = plt.cm.get_cmap('Wistia')
		df["vaestolog"] = df["vaesto"]
		df["vaestolog"] = df["vaestolog"].apply(lambda x: math.log(x))

		padding = df["vaestolog"].mean()/2
		vmin = df["vaesto"].argmin()
		vmax = df["vaesto"].argmax()

		plt.scatter(df.xkoord, df.ykoord, c=df["vaesto"], s=25, alpha=1, cmap = cm,vmin = vmin, vmax = vmax, zorder=1)


print("execute main")
plotMetropolitan(scatterMap=False,annotate=False, numberOfK=5)
print("done")