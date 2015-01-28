import os
from pymongo import Connection
from datetime import datetime

startTime = datetime.now()

p = "41.95949,-115.42236000000001:36.99378,-114.06006000000001:36.97623,-109.11621000000001:42.39912,-109.07227"
state = "UT"

path = r'/Users/mattroesener/Documents/AllStates_20141202'

con = Connection()

db = con.USA1

places = db.places

def reader():
	for dir in os.listdir(path):
		dir_entry_path = os.path.join(path, dir)

		file = open(dir_entry_path, 'r')
		for line in file:
			try:
				newLine = line.split('|')
				if newLine[2] == ("Populated Place" or "Civil"):
					name = newLine[1].replace('Condominium', '').replace('Condo', '')
					long = float(newLine[10])
					lat = float(newLine[9])
					places.insert({'name':name,'class':newLine[2],'state':newLine[3],'loc': {'type':'Point','coordinates':[long, lat]}})
				else:
					pass
			except:
				pass

def distinctData():
	data = db.places.find().distinct("name")
	return data

def polygon():
	list = []
	data = db.places.find(
	  {
	     'loc': {
	       '$geoWithin': { '$polygon': [[-115.42236000000001, 41.95949],
										[-114.06006000000001, 36.99378],
										[-109.11621000000001, 36.97623],
										[-109.07227, 42.39912],
										[-115.42236000000001, 41.95949]] }
	     		}
	  }
	)
	for doc in data:
		name = doc['name']
		list.append(name)

	print len(list)
	return list

def allData():
	#list = []
	data = db.places.find()
	#for item in data:
	#	name = item['name']
	#	list.append(name)

	#list = [i['name'] for i in data]
	list = map(lambda z: z['name'], data)
	#print list
	return list

def checkData():
	#duplicates1 = []
	#originals1 = []

	#for i in polygon():
	#	count = allData().count(i)
	#	if count > 1:
	#		duplicates1.append(i)
	#	else:
	#		originals1.append(i)

	duplicates1 = [x for x in polygon() if allData().count(x) > 1]

	print duplicates1

	originals1 = [x for x in polygon() if allData().count(x) <= 1]

	print originals1

	duplicates = ', '.join(duplicates1)
	originals = ', '.join(originals1)
	print len(duplicates)
	print len(originals)

	return duplicates, originals

def writeCSDL():

	duplicates1 = []
	originals1 = []

	for i in polygon():
		count = allData().count(i)
		if count > 1:
			duplicates1.append(i)
			#print i
			#print "duplicates ", i
		else:
			originals1.append(i)
			#print i
			#print "originals ", i

	duplicates = ', '.join(duplicates1)
	originals = ', '.join(originals1)
	print len(originals)
	print len(duplicates)


	file_name = "geo_file_test1.csdl"

	csdl_file = open(file_name, 'w')

	csdl_file.write("(\n")
	csdl_file.write("\tinteraction.geo geo_polygon " + '"' + p + '"' + "\n")
	csdl_file.write("\tor\n")
	csdl_file.write("\ttwitter.place.full_name contains_any " + '"' + originals + '"' + "\n")
	csdl_file.write("\tor\n")
	csdl_file.write("\t(\n")
	csdl_file.write("\t\ttwitter.place.full_name contains_any " + '"' + duplicates + '"' + "\n")
	csdl_file.write("\t\tand\n")
	csdl_file.write("\t\ttwitter.place.full_name " + '"' + state + '"' + "\n")
	csdl_file.write("\t)\n")

	csdl_file.write("\tor\n")
	csdl_file.write("\ttwitter.retweeted.place.full_name contains_any " + '"' + originals + '"' + "\n")
	csdl_file.write("\tor\n")
	csdl_file.write("\t(\n")
	csdl_file.write("\t\ttwitter.retweeted.place.full_name contains_any " + '"' + duplicates + '"' + "\n")
	csdl_file.write("\t\tand\n")
	csdl_file.write("\t\ttwitter.retweeted.place.full_name " + '"' + state + '"' + "\n")
	csdl_file.write("\t)\n")

	csdl_file.write("\tor\n")
	csdl_file.write("\ttwitter.user.location contains_any " + '"' + originals + '"' + "\n")
	csdl_file.write("\tor\n")
	csdl_file.write("\t(\n")
	csdl_file.write("\t\ttwitter.user.location contains_any " + '"' + duplicates + '"' + "\n")
	csdl_file.write("\t\tand\n")
	csdl_file.write("\t\ttwitter.user.location " + '"' + state + '"' + "\n")
	csdl_file.write("\t)\n")

	csdl_file.write("\tor\n")
	csdl_file.write("\ttwitter.retweeted.user.location contains_any " + '"' + originals + '"' + "\n")
	csdl_file.write("\tor\n")
	csdl_file.write("\t(\n")
	csdl_file.write("\t\ttwitter.retweeted.user.location contains_any " + '"' + duplicates + '"' + "\n")
	csdl_file.write("\t\tand\n")
	csdl_file.write("\t\ttwitter.retweeted.user.location " + '"' + state + '"' + "\n")
	csdl_file.write("\t)\n")
	csdl_file.write(")\n")

	csdl_file.write("""and not
	(
	    // State, Abbreviation
	    twitter.user.location contains_any "Alabama, AL, Alaska, AK, Arizona, AZ, Arkansas, AR, California, CA, Colorado, CO, Connecticut, CT, Delaware, DE, Florida, FL, Georgia, GA, Hawaii, HI, Idaho, ID, Illinois, IL, Indiana, IN, Iowa, IA, Kansas, KS, Kentucky, KY, Louisiana, LA, Maine, ME, Maryland, MD, Massachusetts, MA, Michigan, MI, Minnesota, MN, Mississippi, MS, Missouri, MO, Montana, Nebraska, NE, Nevada, NV, New Hampshire, NH, New Jersey, NJ, New Mexico, NM, New York, NY, North Carolina, NC, North Dakota, ND, Ohio, OH, Oklahoma, OK, Oregon, OR, Pennsylvania, PA, Rhode Island, RI, South Carolina, SC, South Dakota, SD, Tennessee, TN, Texas, TX, Vermont, VT, Virginia, VA, Washington, WA, West Virginia, WV, Wisconsin, WI, Wyoming, WY, District of Columbia, DC"
	    or
	    twitter.retweet.user.location contains_any "Alabama, AL, Alaska, AK, Arizona, AZ, Arkansas, AR, California, CA, Colorado, CO, Connecticut, CT, Delaware, DE, Florida, FL, Georgia, GA, Hawaii, HI, Idaho, ID, Illinois, IL, Indiana, IN, Iowa, IA, Kansas, KS, Kentucky, KY, Louisiana, LA, Maine, ME, Maryland, MD, Massachusetts, MA, Michigan, MI, Minnesota, MN, Mississippi, MS, Missouri, MO, Montana, Nebraska, NE, Nevada, NV, New Hampshire, NH, New Jersey, NJ, New Mexico, NM, New York, NY, North Carolina, NC, North Dakota, ND, Ohio, OH, Oklahoma, OK, Oregon, OR, Pennsylvania, PA, Rhode Island, RI, South Carolina, SC, South Dakota, SD, Tennessee, TN, Texas, TX, Vermont, VT, Virginia, VA, Washington, WA, West Virginia, WV, Wisconsin, WI, Wyoming, WY, District of Columbia, DC"
	    or
	    twitter.retweeted.user.location contains_any "Alabama, AL, Alaska, AK, Arizona, AZ, Arkansas, AR, California, CA, Colorado, CO, Connecticut, CT, Delaware, DE, Florida, FL, Georgia, GA, Hawaii, HI, Idaho, ID, Illinois, IL, Indiana, IN, Iowa, IA, Kansas, KS, Kentucky, KY, Louisiana, LA, Maine, ME, Maryland, MD, Massachusetts, MA, Michigan, MI, Minnesota, MN, Mississippi, MS, Missouri, MO, Montana, Nebraska, NE, Nevada, NV, New Hampshire, NH, New Jersey, NJ, New Mexico, NM, New York, NY, North Carolina, NC, North Dakota, ND, Ohio, OH, Oklahoma, OK, Oregon, OR, Pennsylvania, PA, Rhode Island, RI, South Carolina, SC, South Dakota, SD, Tennessee, TN, Texas, TX, Vermont, VT, Virginia, VA, Washington, WA, West Virginia, WV, Wisconsin, WI, Wyoming, WY, District of Columbia, DCa"
	    or
	    twitter.place.full_name contains_any "Alabama, AL, Alaska, AK, Arizona, AZ, Arkansas, AR, California, CA, Colorado, CO, Connecticut, CT, Delaware, DE, Florida, FL, Georgia, GA, Hawaii, HI, Idaho, ID, Illinois, IL, Indiana, IN, Iowa, IA, Kansas, KS, Kentucky, KY, Louisiana, LA, Maine, ME, Maryland, MD, Massachusetts, MA, Michigan, MI, Minnesota, MN, Mississippi, MS, Missouri, MO, Montana, Nebraska, NE, Nevada, NV, New Hampshire, NH, New Jersey, NJ, New Mexico, NM, New York, NY, North Carolina, NC, North Dakota, ND, Ohio, OH, Oklahoma, OK, Oregon, OR, Pennsylvania, PA, Rhode Island, RI, South Carolina, SC, South Dakota, SD, Tennessee, TN, Texas, TX, Vermont, VT, Virginia, VA, Washington, WA, West Virginia, WV, Wisconsin, WI, Wyoming, WY, District of Columbia, DC"
	    or
	    twitter.retweeted.place.full_name contains_any "Alabama, AL, Alaska, AK, Arizona, AZ, Arkansas, AR, California, CA, Colorado, CO, Connecticut, CT, Delaware, DE, Florida, FL, Georgia, GA, Hawaii, HI, Idaho, ID, Illinois, IL, Indiana, IN, Iowa, IA, Kansas, KS, Kentucky, KY, Louisiana, LA, Maine, ME, Maryland, MD, Massachusetts, MA, Michigan, MI, Minnesota, MN, Mississippi, MS, Missouri, MO, Montana, Nebraska, NE, Nevada, NV, New Hampshire, NH, New Jersey, NJ, New Mexico, NM, New York, NY, North Carolina, NC, North Dakota, ND, Ohio, OH, Oklahoma, OK, Oregon, OR, Pennsylvania, PA, Rhode Island, RI, South Carolina, SC, South Dakota, SD, Tennessee, TN, Texas, TX, Vermont, VT, Virginia, VA, Washington, WA, West Virginia, WV, Wisconsin, WI, Wyoming, WY, District of Columbia, DC"
	    or
	    twitter.user.location cs contains_any "MT"
	    or
	    twitter.retweet.user.location cs contains_any "MT"
	    or
	    twitter.retweeted.user.location cs contains_any "MT"
	    or
	    twitter.place.full_name cs contains_any "MT"
	    or
	    twitter.retweeted.place.full_name cs contains_any "MT"
	    or
	    // Capitals and Largest Cities
	    // note: to edit this section, go into data folder -> news -> local -> Blocklist - States/Capitals/Cities spreadsheet.  Filter 'State' column for the state of the city being worked on and the 'City' column will show the cities listed in the block list for that state.
	    twitter.user.location contains_any "Birmingham, Montgomery, Mobile, Huntsville, Anchorage, Juneau, Phoenix, Tucson, Mesa, Chandler, Glendale, Gilbert, Scottsdale, Tempe, Peoria, Surprise, Little Rock, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, Fremont, San Bernardino, Modesto, Oxnard, Fontana, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Oceanside, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Corona, Palmdale, Salinas, Hayward, Pomona, Escondido, Sunnyvale, Torrance, Orange, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Concord, Victorville, Santa Clara, Vallejo, Berkeley, El Monte, Downey, Costa Mesa, Inglewood, Carlsbad, Fairfield, Ventura, West Covina, Richmond, Murrieta, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Thornton, Arvada, Westminster, Pueblo, Centennial, Boulder, Bridgeport, New Haven, Stamford, Waterbury, Hartford, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Tallahassee, Atlanta, Columbus, Augusta, Savannah, Athens, Honolulu, Boise, Chicago, Aurora, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Davenport, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Baton Rouge, Shreveport, Lafayette, Augusta, Baltimore, Annapolis, Boston, Worcester, Lowell, Cambridge, Detroit, Grand Rapids, Warren, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Saint Paul, Rochester, St. Paul, Jackson, Kansas City, St. Louis, Independence, Columbia, Jefferson City, Billings, Helena, Omaha, Lincoln, Las Vegas, Henderson, Reno, Carson City, Manchester, Concord, Newark, Jersey City, Paterson, Elizabeth, Edison, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, Charlotte, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Cary, Wilmington, High Point, Raleigh, Fargo, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Norman, Broken Arrow, Portland, Salem, Eugene, Gresham, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Providence, Columbia, Charleston, Sioux Falls, Pierre, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, Pasadena, McKinney, Mesquite, Killeen, Frisco, McAllen, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Richardson, Lewisville, Tyler, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Richmond, Newport News, Alexandria, Hampton, Seattle, Spokane, Tacoma, Vancouver, Bellevue, Kent, Everett, Olympia, Milwaukee, Madison, Green Bay, Cheyenne"
	    or
	    twitter.retweet.user.location contains_any "Birmingham, Montgomery, Mobile, Huntsville, Anchorage, Juneau, Phoenix, Tucson, Mesa, Chandler, Glendale, Gilbert, Scottsdale, Tempe, Peoria, Surprise, Little Rock, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, Fremont, San Bernardino, Modesto, Oxnard, Fontana, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Oceanside, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Corona, Palmdale, Salinas, Hayward, Pomona, Escondido, Sunnyvale, Torrance, Orange, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Concord, Victorville, Santa Clara, Vallejo, Berkeley, El Monte, Downey, Costa Mesa, Inglewood, Carlsbad, Fairfield, Ventura, West Covina, Richmond, Murrieta, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Thornton, Arvada, Westminster, Pueblo, Centennial, Boulder, Bridgeport, New Haven, Stamford, Waterbury, Hartford, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Tallahassee, Atlanta, Columbus, Augusta, Savannah, Athens, Honolulu, Boise, Chicago, Aurora, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Davenport, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Baton Rouge, Shreveport, Lafayette, Augusta, Baltimore, Annapolis, Boston, Worcester, Lowell, Cambridge, Detroit, Grand Rapids, Warren, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Saint Paul, Rochester, St. Paul, Jackson, Kansas City, St. Louis, Independence, Columbia, Jefferson City, Billings, Helena, Omaha, Lincoln, Las Vegas, Henderson, Reno, Carson City, Manchester, Concord, Newark, Jersey City, Paterson, Elizabeth, Edison, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, Charlotte, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Cary, Wilmington, High Point, Raleigh, Fargo, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Norman, Broken Arrow, Portland, Salem, Eugene, Gresham, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Providence, Columbia, Charleston, Sioux Falls, Pierre, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, Pasadena, McKinney, Mesquite, Killeen, Frisco, McAllen, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Richardson, Lewisville, Tyler, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Newport News, Alexandria, Hampton, Richmond, Seattle, Spokane, Tacoma, Vancouver, Bellevue, Kent, Everett, Olympia, Milwaukee, Madison, Green Bay, Cheyenne"
	    or
	    twitter.retweeted.user.location contains_any "Birmingham, Montgomery, Mobile, Huntsville, Anchorage, Juneau, Phoenix, Tucson, Mesa, Chandler, Glendale, Gilbert, Scottsdale, Tempe, Peoria, Surprise, Little Rock, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, Fremont, San Bernardino, Modesto, Oxnard, Fontana, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Oceanside, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Corona, Palmdale, Salinas, Hayward, Pomona, Escondido, Sunnyvale, Torrance, Orange, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Concord, Victorville, Santa Clara, Vallejo, Berkeley, El Monte, Downey, Costa Mesa, Inglewood, Carlsbad, Fairfield, Ventura, West Covina, Richmond, Murrieta, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Thornton, Arvada, Westminster, Pueblo, Centennial, Boulder, Bridgeport, New Haven, Stamford, Waterbury, Hartford, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Tallahassee, Atlanta, Columbus, Augusta, Savannah, Athens, Honolulu, Boise, Chicago, Aurora, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Davenport, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Baton Rouge, Shreveport, Lafayette, Augusta, Baltimore, Annapolis, Boston, Worcester, Lowell, Cambridge, Detroit, Grand Rapids, Warren, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Saint Paul, Rochester, St. Paul, Jackson, Kansas City, St. Louis, Independence, Columbia, Jefferson City, Billings, Helena, Omaha, Lincoln, Las Vegas, Henderson, Reno, Carson City, Manchester, Concord, Newark, Jersey City, Paterson, Elizabeth, Edison, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, Charlotte, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Cary, Wilmington, High Point, Raleigh, Fargo, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Norman, Broken Arrow, Portland, Salem, Eugene, Gresham, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Providence, Columbia, Charleston, Sioux Falls, Pierre, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, Pasadena, McKinney, Mesquite, Killeen, Frisco, McAllen, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Richardson, Lewisville, Tyler, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Richmond, Newport News, Alexandria, Hampton, Seattle, Spokane, Tacoma, Vancouver, Bellevue, Kent, Everett, Olympia, Milwaukee, Madison, Green Bay, Cheyenne"
	    or
	    twitter.place.full_name contains_any "Birmingham, Montgomery, Mobile, Huntsville, Anchorage, Juneau, Phoenix, Tucson, Mesa, Chandler, Glendale, Gilbert, Scottsdale, Tempe, Peoria, Surprise, Little Rock, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, Fremont, San Bernardino, Modesto, Oxnard, Fontana, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Oceanside, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Corona, Palmdale, Salinas, Hayward, Pomona, Escondido, Sunnyvale, Torrance, Orange, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Concord, Victorville, Santa Clara, Vallejo, Berkeley, El Monte, Downey, Costa Mesa, Inglewood, Carlsbad, Fairfield, Ventura, West Covina, Richmond, Murrieta, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Thornton, Arvada, Westminster, Pueblo, Centennial, Boulder, Bridgeport, New Haven, Stamford, Waterbury, Hartford, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Tallahassee, Atlanta, Columbus, Augusta, Savannah, Athens, Honolulu, Boise, Chicago, Aurora, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Davenport, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Baton Rouge, Shreveport, Lafayette, Augusta, Baltimore, Annapolis, Boston, Worcester, Lowell, Cambridge, Detroit, Grand Rapids, Warren, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Saint Paul, Rochester, St. Paul, Jackson, Kansas City, St. Louis, Independence, Columbia, Jefferson City, Billings, Helena, Omaha, Lincoln, Las Vegas, Henderson, Reno, Carson City, Manchester, Concord, Newark, Jersey City, Paterson, Elizabeth, Edison, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, Charlotte, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Cary, Wilmington, High Point, Raleigh, Fargo, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Norman, Broken Arrow, Portland, Salem, Eugene, Gresham, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Providence, Columbia, Charleston, Sioux Falls, Pierre, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, Pasadena, McKinney, Mesquite, Killeen, Frisco, McAllen, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Richardson, Lewisville, Tyler, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Richmond, Newport News, Alexandria, Hampton, Seattle, Spokane, Tacoma, Vancouver, Bellevue, Kent, Everett, Olympia, Milwaukee, Madison, Green Bay, Cheyenne"
	    or
	    twitter.retweeted.place.full_name contains_any "Birmingham, Montgomery, Mobile, Huntsville, Anchorage, Juneau, Phoenix, Tucson, Mesa, Chandler, Glendale, Gilbert, Scottsdale, Tempe, Peoria, Surprise, Little Rock, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Sacramento, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, Fremont, San Bernardino, Modesto, Oxnard, Fontana, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Oceanside, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Corona, Palmdale, Salinas, Hayward, Pomona, Escondido, Sunnyvale, Torrance, Orange, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Concord, Victorville, Santa Clara, Vallejo, Berkeley, El Monte, Downey, Costa Mesa, Inglewood, Carlsbad, Fairfield, Ventura, West Covina, Richmond, Murrieta, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Thornton, Arvada, Westminster, Pueblo, Centennial, Boulder, Bridgeport, New Haven, Stamford, Hartford, Waterbury, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Tallahassee, Atlanta, Columbus, Augusta, Savannah, Athens, Honolulu, Boise, Chicago, Aurora, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Davenport, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Baton Rouge, Shreveport, Lafayette, Augusta, Baltimore, Annapolis, Boston, Worcester, Lowell, Cambridge, Detroit, Grand Rapids, Warren, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Saint Paul, Rochester, St. Paul, Jackson, Kansas City, St. Louis, Independence, Columbia, Jefferson City, Billings, Helena, Omaha, Lincoln, Las Vegas, Henderson, Reno, Carson City, Manchester, Concord, Newark, Jersey City, Paterson, Elizabeth, Edison, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Buffalo, Rochester, Yonkers, Syracuse, Albany, Charlotte, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Cary, Wilmington, High Point, Raleigh, Fargo, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Norman, Broken Arrow, Portland, Salem, Eugene, Gresham, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Providence, Columbia, Charleston, Sioux Falls, Pierre, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Austin, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Garland, Irving, Amarillo, Grand Prairie, Brownsville, Pasadena, McKinney, Mesquite, Killeen, Frisco, McAllen, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Richardson, Lewisville, Tyler, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Richmond, Newport News, Alexandria, Hampton, Seattle, Spokane, Tacoma, Vancouver, Bellevue, Kent, Everett, Olympia, Milwaukee, Madison, Green Bay, Cheyenne"
	    or
	    // Block mentions of states or large cities
	    // Removed state and city names that could be used as names or are too-common words: Georgia, Indiana, Montana, Tennessee, Virginia, Washington, Montgomery, Mobile, Juneau, Phoenix, Mesa, Chandler, Surprise, Little Rock, Fremont, Fontana, Oceanside, Corona, Salinas, Hayward, Orange, Concord, Vallejo, Berkeley, Downey, Ventura, Torrance, Richmond, Murrieta, Thornton, Westminster, Pueblo, Centennial, Boulder, Columbus, Augusta, Aurora, Davenport, Lafayette, Augusta, Worcester, Lowell, Warren, Rochester, Saint Paul, St. Paul, Jackson, Columbia, Billings, Helena, Lincoln, Henderson, Manchester, Concord, Paterson, Elizabeth, Edison, Buffalo, Charlotte, Cary, High Point, Fargo, Norman, Salem, Eugene, Gresham, Providence, Pierre, Austin, Garland, Irving, McKinney, Mesquite, McAllen, Richardson, Tyler, Alexandria, Richmond, Kent, Madison, Cheyenne, Savannah, Tacoma
	    interaction.content contains_any "Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware, Florida, Hawaii, Idaho, Illinois, Iowa, Kansas, Kentucky, Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi, Missouri, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico, New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania, Rhode Island, South Carolina, South Dakota, Texas, Vermont, West Virginia, Wisconsin, Wyoming, District of Columbia"
	    or
	    interaction.content cs contains_any "NY"
	    or
	    interaction.content contains_any "Birmingham, Huntsville, Anchorage, Tucson, Gilbert, Scottsdale, Tempe, Peoria, Los Angeles, San Diego, San Jose, San Francisco, Fresno, Long Beach, Oakland, Bakersfield, Anaheim, Santa Ana, Riverside, Stockton, Chula Vista, Irvine, San Bernardino, Modesto, Oxnard, Moreno Valley, Huntington Beach, Glendale, Santa Clarita, Garden Grove, Santa Rosa, Rancho Cucamonga, Ontario, Elk Grove, Lancaster, Palmdale, Pomona, Escondido, Sunnyvale, Pasadena, Fullerton, Thousand Oaks, Visalia, Roseville, Simi Valley, Victorville, Santa Clara, El Monte, Costa Mesa, Inglewood, Carlsbad, Fairfield, West Covina, Antioch, Temecula, Norwalk, Daly City, Burbank, Santa Maria, El Cajon, Rialto, San Mateo, Sacramento, Denver, Aurora, Fort Collins, Lakewood, Arvada, Bridgeport, New Haven, Stamford, Waterbury, Hartford, Dover, Jacksonville, Miami, Tampa, Orlando, St. Petersburg, Hialeah, Tallahassee, Fort Lauderdale, Ft. Lauderdale, Port St. Lucie, Cape Coral, Pembroke Pines, Hollywood, Miramar, Gainesville, Coral Springs, Miami Gardens, Clearwater, Palm Bay, Pompano Beach, West Palm Beach, Lakeland, Atlanta, Athens, Honolulu, Boise, Chicago, Rockford, Joliet, Naperville, Springfield, Peoria, Elgin, Indianapolis, Fort Wayne, Evansville, South Bend, Indianapolis, Des Moines, Cedar Rapids, Wichita, Overland Park, Kansas City, Olathe, Topeka, Louisville, Lexington, Frankfort, New Orleans, Shreveport, Baton Rouge, Baltimore, Annapolis, Boston, Cambridge, Detroit, Grand Rapids, Sterling Heights, Ann Arbor, Lansing, Minneapolis, Kansas City, St. Louis, Independence, Jefferson City, Omaha, Las Vegas, Reno, Carson City, Newark, Jersey City, Trenton, Albuquerque, Las Cruces, Santa Fe, New York City, Rochester, Yonkers, Syracuse, Albany, Raleigh, Greensboro, Durham, Winston-Salem, Fayetteville, Wilmington, Raleigh, Bismarck, Columbus, Cleveland, Cincinnati, Toledo, Akron, Dayton, Oklahoma City, Tulsa, Broken Arrow, Portland, Philadelphia, Pittsburgh, Allentown, Erie, Harrisburg, Columbia, Charleston, Sioux Falls, Memphis, Nashville, Knoxville, Chattanooga, Clarksville, Murfreesboro, Houston, San Antonio, Dallas, Fort Worth, El Paso, Arlington, Corpus Christi, Plano, Laredo, Lubbock, Amarillo, Grand Prairie, Brownsville, Killeen, Frisco, Waco, Carrollton, Midland, Denton, Abilene, Beaumont, Odessa, Round Rock, Wichita Falls, Lewisville, Pearland, College Station, Burlington, Montpelier, Virginia Beach, Norfolk, Chesapeake, Richmond, Newport News, Hampton, Seattle, Spokane, Vancouver, Bellevue, Everett, Olympia, Milwaukee, Green Bay"
	)""")

	csdl_file.close()

#reader()
#polygon()
checkData()
#writeCSDL()
#distinctData()
#allData()
print "Overall Script: ", datetime.now() - startTime