import requests 
import collections

SEAT_LIMIT=100

URL="http://0.0.0.0:5000"


movies = []
#Post some movies
try:
	movie = {"name": "Parasite", "date": "03.03.2020", "time": "20:00"}
	response = requests.post((URL+"/movies"), json = movie)
	if response.status_code == 201:
		content = response.json()
		movie["screen_no"] = content["screen_no"]
		movies.append(movie)
	else: raise Exception("First post fails") 	

	movie = {"name": "The Gentlemen", "date": "03.03.2020", "time": "22:15"}	
	response = requests.post((URL+"/movies"), json=movie)
	if response.status_code == 201:
		content = response.json()
		movie["screen_no"] = content["screen_no"]
		movies.append(movie)
	else: raise Exception("Second post fails") 	
	
	for i in range(0,31):
		movie = {"name": "The Gentlemen", "date": '{0:02d}'.format(i+1)+".03.2020", "time": "22:15"}	
		response = requests.post((URL+"/movies"), json=movie)

		if response.status_code == 201:
			content = response.json()
			movie["screen_no"] = content["screen_no"]
			movies.append(movie)
		else: raise Exception("First loop fails") 	
	
	for i in range(0,31):
		movie = {"name": "It must be heaven", "date": '{0:02d}'.format(i+1)+".03.2020", "time": "18:30"}	
		response = requests.post((URL+"/movies"), json=movie)
		if response.status_code == 201:
			content = response.json()
			movie["screen_no"] = content["screen_no"]
			movies.append(movie)
		else: raise Exception("Second loop fails") 	
			
	print ("Test 1 succeeds")		
except Exception as e:
	print(str(e))
	print ("Test 1 fails")


#Check if the movies exist in the D.B.
try:
	if len(movies) < 2:
		raise Exception("Not sufficient for Test 2")
	response = requests.get((URL+"/movies"))
	if response.status_code != 200:
		raise Exception("Unexpected return code")
	result = response.json()
	#del result[0]
	pairs=zip(movies, result)
	if any(x != y for x, y in pairs):
		raise Exception("Result is not equal to local copy")
	print("Test 2 succeeds")
except Exception as e:
	print(str(e))
	print ("Test 2 fails")


#Get non-existing items again
try:
	response = requests.get((URL+"/movies/Gora/01.01.2020"))
	if response.status_code != 404:
		raise Exception("Invalid return code: try1")
	response = requests.get((URL+"/movies/Arog/01.01/2020"))
	if response.status_code != 404:
		raise Exception("Invalid return code: try2")
		
	for movie in movies:
		response = requests.get((URL+"/movies/"+movie["name"]+"/"+movie["date"]))
		if response.status_code != 200:
			raise Exception("Invalid return code (screen no: "+movie["screen_no"]+")")
		if movie not in response.json():
			raise Exception("Reponse does not include test item "+movie["screen_no"])

	print("Test 3 succeeds")
except Exception as e:
	print(str(e))
	print ("Test 3 fails")		
		
#Delete some movies		
try:
	for i in range(10):
		response = requests.delete(URL+"/movies/"+movies[len(movies)-1-i]["name"]+"/"+movies[len(movies)-1-i]["date"])
		if response.status_code != 200:
			raise Exception("Invalid return code in deletion")


	print("Test 4 succeeds")
except Exception as e:
	print(str(e))
	print ("Test 4 fails")			

		
#make reservation to non-existing movies
try:
	for i in range(10):
		response = requests.post((URL+"/ticket"), json=movies[len(movies)-1-i])
		if response.status_code != 404:
			raise Exception("Invalid return code for non existing screen no at /tickets")
	print("Test 5 succeeds")
except Exception as e:
	print(str(e))
	print ("Test 5 fails")	


		
#make reservations for valid movies
reservations=[]
try:
	for i in range(3):
		response = requests.post((URL+"/ticket"), json=movies[i])
		if response.status_code != 201:
			raise Exception("Invalid return code for existing screen no at /tickets, iter: " + str(i))
		else:
			reservations.append(response.json())
	print("Test 6 succeeds")		
except Exception as e:
	print(str(e))
	print ("Test 6 fails")	
		
	
		
#overload		
try:
	for i in range(SEAT_LIMIT):
		response = requests.post((URL+"/ticket"), json=movies[5])
		
		if response.status_code != 201:
			raise Exception("Invalid return code at iter: "+str(i))
		else:
			reservations.append(response.json())
	for i in range(10):
		response = requests.post((URL+"/ticket"), json=movies[5])
		if response.status_code != 409:
			raise Exception("Invalid return code at for overbooked session")

	print("Test 7 succeeds")		
except Exception as e:
	print(str(e))
	print ("Test 7 fails")				

#view reservations	
try:
	if(len(reservations) < 3):
		raise Exception("Insufficient number of reservations to do Test 8")
	for reservation in reservations:
		response = requests.get((URL+"/ticket"), json={"reservation_no":reservation["reservation_no"]})
		if(response.status_code!=200):
			raise Exception("Invalid return code for existing reservation")
			
	response = requests.get((URL+"/ticket"), json={"reservation_no":"ZAAAA"})
	if(response.status_code!=404):
		raise Exception("Invalid return code for non-existing reservation")
	print("Test 8 succeeds")			
except Exception as e:
	print(str(e))
	print ("Test 8 fails")				

#view all reservations	
try:
	response = requests.get((URL+"/ticket"))
	print(response.json())
	reservation_nos_local=list(map(lambda x:x["reservation_no"],reservations))
	reservation_nos_server=list(map(lambda x:x["reservation_no"],response.json()))
	print(reservation_nos_local, reservation_nos_server)
	pairs=zip(reservation_nos_local, reservation_nos_server)
	if any(x != y for x, y in pairs):
		raise Exception("Result is not equal to local copy")

	print("Test 9 succeeds")
			
except Exception as e:
	print(str(e))

	print ("Test 9 fails")	

#change seat_no	
try:
	response = requests.post((URL+"/ticket"), json=movies[15])
	res_no1=0
	seat_no1=0
	res_no2=0
	seat_no2=0
	if(response.status_code==201):
		res_no1=response.json()["reservation_no"]
		response1 = requests.get((URL+"/ticket"), json={"reservation_no":res_no1})
		seat_no1=response1.json()["seat_no"]
	else: raise Exception("Invalid response code for post 1")
		
	response = requests.post((URL+"/ticket"), json=movies[15])
	if(response.status_code==201):
		res_no2=response.json()["reservation_no"]
		response1 = requests.get((URL+"/ticket"), json={"reservation_no":res_no2})
		seat_no2=response1.json()["seat_no"]	
	else: raise Exception("Invalid response code for post 2")
	response = requests.put((URL+"/ticket"), json={"reservation_no":res_no1, "seat_no":seat_no2})
	if(response.status_code!=409):
		raise Exception("This change seat must be unavailible")
	
	found=False
	for i in range(SEAT_LIMIT):	
		response = requests.put((URL+"/ticket"), json={"reservation_no":res_no1, "seat_no":i})
		if(response.status_code==200):
			found=True
			break
	if not found: raise Exception("This change seat must be availible")

	response = requests.put((URL+"/ticket"), json={"reservation_no":"BBBB", "seat_no":seat_no2+1})
	if(response.status_code!=404):
		raise Exception("This should be invalid res_no")
	print("Test 10 succeeds")	
except Exception as e:
	print(str(e))
	print ("Test 10 fails")				

		
#cancel reservation tests
try:	
	response = requests.delete((URL+"/ticket"), json={"reservation_no":reservations[0]["reservation_no"]})
	if(response.status_code!=200):
		raise Exception("Invalid return code")
		
	response = requests.get((URL+"/ticket"), json={"reservation_no":reservations[0]["reservation_no"]})
	if(response.status_code!=404):
		raise Exception("Invalid return code for deleted reservation")
	response = requests.delete((URL+"/ticket"), json={"reservation_no":"KKKK"})
	if(response.status_code!=404):
		raise Exception("Invalid return code for never existed reservation")

	print("Test 11 succeeds")
except Exception as e:
	print(str(e))
	print ("Test 11 fails")				

		
		
		
		
		
