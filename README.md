# IntroData
Course project for Introduction to Data Science

# Some useful git commands

`git clone [repository path, here: https://github.com/sasumaki/IntroData.git]` Clones the repository to the folder that you are in.

`git status` Repository status (new files? uncommitted files? Any news?)

`git pull` get changes from repository and update your local codes (also `git fetch` + `git rebase origin/master`)

`git add .` add all files that you want to commit and which were listed with `git status`

`git add [filename]` add but only one file

`git commit -m "[what did you change?]"` create a version of the file

`git push origin` push your changes to repository so that they're visible to others.

Data: http://geo.stat.fi/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=vaki2016_1km_kp&outputFormat=csv

Kuntajako kartalle: http://geoserv.stat.fi:8080/geoserver/tilastointialueet/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=tilastointialueet:kunta1000k_2017&outputFormat=csv

Espoon rakennukset: http://geoserver.hel.fi/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=osm:esp_rakennukset_dist&outputFormat=json
Vantaan rakennukset: korvaa esp-->van
Helsingin rakennukset: korvaa esp--> hel (huom, ei toimi)
