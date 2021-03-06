import time
from flask import  Flask, jsonify, request
from controller.bus_and_stop import *
from controller.getBusData import *

app = Flask(__name__)

red_stop, red_dist = init_red()
blue_stop, blue_dist=init_blue()
'''with open('red_dist.json','w') as f:
	json.dump(red_dist,f)
blue_stop, blue_dist = init_blue()
with open('blue_dist.json','w') as f:
	json.dump(blue_dist,f)'''
#for i in blue_stop:
#	print(i.name, i.pos, i.line, i.fake, i.code)
#print(blue_dist)

@app.route("/")
def hello():
	return 'hello'


stopName = 'Lee Wee Nam Library'

@app.route('/todo/api/v1.0/eta', methods=['GET'])
def ETA():
	for i in red_stop:
		#print(i.name)
		if (i.name == stopName or i.code == stopName):
			eta, bus = bus_queue(red_stop, red_dist, "Red", i.code)
			#print(eta)
			flag=True
			for i in range(len(eta)):
				Dist, index=eta[i]
				if int(bus[index]["speed"])==0:
					eta[i]="--"
					flag=False
					continue
				eta[i]=3.6*Dist/float(bus[index]["speed"])/60
				if i and flag:
					if eta[i]<eta[i-1]:
						eta[i]=eta[i-1]
				flag=True
			#eta, tmp=dumb(eta, i.pos, stop_pos, bus)
			return jsonify(eta)


@app.route('/todo/api/v1.0/init',methods=['GET'])
def INIT():
	bus = Bus()
	bus.update_response()
	blueBus = bus.get_blue()
	redBus = bus.get_red()
	return jsonify(blueBus,redBus)


yourLocation = [
	{
		"lat" : 1.3478803,
		"lon": 103.687008,
		"destStop" : 'Innovation Centre'
	}
]

@app.route('/todo/api/v1.0/gotolocation', methods=['GET'])
def goToLocation():
	flag = False

	while ( not flag):
		for i in red_stop:
			if (yourLocation[0]['destStop'] == i.name):
				line = i.line
				flag = True
				break

		for i in blue_stop:
			if (yourLocation[0]['destStop'] == i.name):
				line = i.line
				flag = True
				break

	if (line == 'Red'):
		nearStop = get_nearest_bus_stop(yourLocation[0]['lon'],yourLocation[0]['lat'],red_stop,'walking')
	else:
		nearStop = get_nearest_bus_stop(yourLocation[0]['lon'],yourLocation[0]['lat'],blue_stop,'walking')

	etaToNear, bus = bus_queue(red_stop, red_dist, nearStop.line, nearStop.code)

	destInfo = getStopInfo(yourLocation[0]['destStop'], line, red_stop, blue_stop)
	#etaToDest = bus_queue(red_stop, red_dist, destInfo.line,destInfo.code)
	etaToNear, etaToDest = dumb(etaToNear, nearStop.pos, destInfo.pos, bus)
	orgPos=(yourLocation[0]['lon'], yourLocation[0]['lat'])
	wTime = walkTime(orgPos, destInfo.pos)
	# etaToNear = [4.7, '--', 9.6, 9.6, 15.57]
	# etaToDest = [4.7, '--', 9.6, 9.6, 15.57]

	# for i in range(len(etaToNear)):
	# 	if (etaToDest[i] == '--' or etaToNear == '--'):
	# 		pass
	# 	else:
	# 		etaToDest[i] = etaToNear[i] + etaToDest[i]
	result = [
		{
			'walk time' : wTime,
			'bus arrival time' : etaToNear,
			'total time by bus' : etaToDest
		}
	]
	# print('Sleep')
	# time.sleep(30)
	# print("Wake Up")
	return jsonify(result)

destFake = [
	{
		"code" : '27011'
	}
]

@app.route('/todo/api/v1.0/notify', methods=['POST','GET'])
def notify():
	j = destFake[0]['code']
	print(j)
	stops=[]
	for i in red_stop:
		if j == i.code:
			stops=red_stop
			break
	if stops==[]:
		stops=blue_stop
	if request.method == 'POST':
		while(True):
			time.sleep(10)
			orgPos=(yourLocation[0]['lon'], yourLocation[0]['lat'])
			if (judge(destFake[0]['code'], orgPos, stops)):
				return "GET OUT"



if __name__ == '__main__':
	app.run(debug=True)
