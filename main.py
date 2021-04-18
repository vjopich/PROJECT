import gpxpy
import gpxpy.gpx
from simplekml import Kml
from geographiclib.geodesic import Geodesic
from math import sin, cos, atan2, sqrt, degrees

# kmps = 10
# inp = '2_brata.gpx'#'sample-gpx/RoscoffCoastal/Lannion_Plestin_parcours24.4RE.gpx'
inp = input('Введите полное имя входного файла: ')
kmps = float(input('Введите скорость, км/с (=1): ') or 1)
angle = float(input('Введите угол к земле, в градусах (=80): ') or 80)
height = float(input('Введите высоту над землей (=50): ') or 50)
export = input('Введите имя выходного файла (=имя входного + расширение): ') or inp.replace('.gpx', '.kml')

def getDistance(p1, p2): # получение расстояния. 
	R = 6373.0
	dlon = p1['lo'] - p2['lo']
	dlat = p1['la'] - p2['la']

	a = sin(dlat / 2)**2 + cos(p1['la']) * cos(p2['la']) * sin(dlon / 2)**2
	c = 2 * atan2(sqrt(a), sqrt(1 - a))

	return R * c

def getBearing(p1, p2): # получение азимута
    return Geodesic.WGS84.Inverse(p1['la'], p1['lo'], p2['la'], p2['lo'])['azi1']

tracks = [] # маршруты [точки]
with open(inp, 'rt', encoding='utf-8') as file:
	gpx = gpxpy.parse(file)
	for track in gpx.tracks:
		t = { 'points': [], 'name': track.name }
		for segment in track.segments:
			for point in segment.points:
				t['points'].append({ 'la': point.latitude, 'lo': point.longitude, 'el': point.elevation, 'name': point.name })
		tracks.append(t)

kml = Kml()
for track in tracks:
	tour = kml.newgxtour(name=track['name']) # новый тур
	playlist = tour.newgxplaylist() # сама анимация
	t = kml.newgxtrack(name=track['name']) # след на земле
	for i in range(len(track['points'])):
		point = track['points'][i]

		pnt = t.newgxcoord([(point['lo'], point['la'])]) # точка следа. Широта и долгота наоборот?

		dst, bearing = 1, 0
		if i != len(track['points']) - 1:
			npoint = track['points'][i + 1]
			dst = getDistance(point, npoint)
			bearing = getBearing(point, npoint)

		flyto = playlist.newgxflyto(gxduration=dst / kmps, gxflytomode='smooth') # анимация камеры
		flyto.camera.longitude = point['lo'] # долгота
		flyto.camera.latitude = point['la'] # широта
		flyto.camera.altitude = height # высота над землей
		flyto.camera.heading = bearing # направление камеры (азимут)
		flyto.camera.tilt = angle # угол наклона лицом в землю
		# flyto.camera.roll = 0
		flyto.camera.attitudeMode = 'relativeToGround'
kml.save(export)
