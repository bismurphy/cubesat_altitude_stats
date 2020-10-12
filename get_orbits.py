day_length = 86400 #in seconds
earth_mu = 3.986e14#Standard gravitational parameter
earth_radius = 6371000

class Satellite():
    #Takes a TLE as a list of 3 strings.
    def __init__(self, TLE):
        self.tle = "\n".join(TLE) + "\n"
        self.name = TLE[0][:-1]
        self.line1 = TLE[1]
        self.line2 = TLE[2]
        self.mean_motion = float(self.line2[52:63])
        self.orbital_period = day_length / self.mean_motion
        self.semimajor_axis = (earth_mu * self.orbital_period**2 / (4 * math.pi**2))**(1/3)
        self.sma_altitude = self.semimajor_axis - earth_radius
        self.eccentricity = float("0." + self.line2[26:33])
        self.periapsis = (1-self.eccentricity) * self.semimajor_axis
        self.apoapsis  = (1+self.eccentricity) * self.semimajor_axis
        self.periapsis_altitude = self.periapsis - earth_radius
        self.apoapsis_altitude = self.apoapsis - earth_radius
    def __str__(self):
        return self.name + "\n" + self.line1 + "\n" + self.line2
    
import math
import requests

#This is https://planet4589.org/space/gcat/tsv/cat/satcat.tsv
satcat = open('satcat.tsv','r')
#This list will hold all the satcat identifiers of the cubesats we find.
satcat_nums = []
for row in satcat.readlines()[1:]:
    #Status code of "O" indicates in orbit, still in free flight.
    status_code = row.split("\t")[11]
    if "cubesat" in row.lower() and status_code == "O":
        satcat_nums += [row.split("\t")[1]]
satellites = []
#We don't want to overload Celestrak, so we're going to get the data and then save to a file.
#Change this to true
fetch_data = False
if(fetch_data):
    for ident in satcat_nums:
        raw_reply = requests.get('https://celestrak.com/satcat/tle.php?CATNR=' + ident).text
        TLE_lines = raw_reply.splitlines()
        print(ident)
        if len(TLE_lines) == 3:
            satellites += [Satellite(TLE_lines)]
        else:
            print(TLE_lines)
    with open('cubesat_tle_list.txt','w') as outfile:
        out_text = ""
        for satellite in satellites:
            out_text += satellite.tle
        outfile.write(out_text)
else:
    #If you're getting a file not found error, you are probably running this script for the first time.
    #Change fetch_data to True above, and that should sort you :)
    with open('cubesat_tle_list.txt','r') as sat_file:
        lines = sat_file.readlines()
        for i in range(0,len(lines),3):
            satellites += [Satellite(lines[i:i+3])]
highest_apos = sorted(satellites, key= lambda x:x.apoapsis_altitude,reverse=True)
lowest_peris = sorted(satellites, key= lambda x:x.periapsis_altitude)
if len(highest_apos) == len(lowest_peris):
    sat_count = len(highest_apos)
else:
    print("Something has gone horribly wrong...")
print(str(sat_count) + " satellites loaded")
margin_size = int(sat_count * .05)

print()
print("Top 5% of cubesats is the top " + str(margin_size))
marginal_high_satellite = highest_apos[margin_size]
print("The " + str(margin_size) + "th highest cubesat is " + marginal_high_satellite.name)
print("which has an apoapsis of " + str(marginal_high_satellite.apoapsis) + "m")
print("which has altitude " + str((marginal_high_satellite.apoapsis - earth_radius) / 1000) + "km")

print()
print("Bottom 5% of cubesats is the bottom " + str(margin_size))
marginal_low_satellite = lowest_peris[margin_size]
print("The " + str(margin_size) + "th lowest cubesat is " + marginal_low_satellite.name)
print("which has a periapsis of " + str(marginal_low_satellite.periapsis) + "m")
print("which has altitude " + str((marginal_low_satellite.periapsis - earth_radius) / 1000) + "km")
