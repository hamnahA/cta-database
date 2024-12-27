# Author:Hamnah Shafiq Ansari
# CS341
#9/19/2024
# project 1 CTA database app
# description: This project is a console-based Python program 
# that allows users to explore and analyze CTA L train ridership data in Chicago. 
# Users can input various commands to view station information, compare ridership statistics,
# and visualize data about the CTA train system.

import sqlite3
import os
import matplotlib.pyplot as plt
import math

# Verify the path to ensure you're using the correct database file
db_path = 'CTA2_L_daily_ridership.db'

# Connect to the correct SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("** Welcome to CTA L analysis app **\n")
print("General Statistics:")

# Number of stations
cursor.execute("SELECT COUNT(Station_Name) FROM Stations")
station_count = cursor.fetchone()[0]
print("  # of stations:", f"{station_count:,}")

# Number of stops
cursor.execute("SELECT COUNT(Stop_Name) FROM Stops")
stop_count = cursor.fetchone()[0]
print("  # of stops:", f"{stop_count:,}")

# Number of ride entries
cursor.execute("SELECT COUNT(Num_Riders) FROM Ridership")
ride_entries = cursor.fetchone()[0]
print("  # of ride entries:", f"{ride_entries:,}")

# Date range from oldest to most recent
cursor.execute("SELECT DISTINCT strftime('%Y-%m-%d', Ride_Date) FROM Ridership ORDER BY Ride_Date ASC")
oldest_date = cursor.fetchone()[0]

cursor.execute("SELECT DISTINCT strftime('%Y-%m-%d', Ride_Date) FROM Ridership ORDER BY Ride_Date DESC")
recent_date = cursor.fetchone()[0]

print("  date range:", oldest_date, "-", recent_date)

# Total ridership
cursor.execute("SELECT SUM(Num_Riders) FROM Ridership")
ridership_count = cursor.fetchone()[0]
print("  Total ridership:", f"{ridership_count:,}")

########################FUNCTIONS##################################
# Functions to handle user inputs
def userinput1func():
    input1= input ("\nEnter partial station name (wildcards _ and %): ")
    
    cursor.execute("SELECT Station_ID, Station_Name from Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC" ,(input1,))
    found_stations=cursor.fetchall()

    if found_stations:
        # print("Matching stations:")
        for  station_ID,station_name in found_stations:
            print(f"{station_ID} :",f"{station_name}")
    else:
        print("**No stations found...")

#function to calculate the command 2
def userinput2func():

    input2 = input("\nEnter the name of the station you would like to analyze: ").strip()#input2 is station name

    #this will help to exact match the station name
    if not input2 or '%' in input2 or '_' in input2:
        print("**No data found...")
        return

    # Use exact match instead of LIKE to avoid wildcard searches
    cursor.execute("SELECT Station_ID from Stations WHERE Station_Name = ?" , (input2,))
    data_found = cursor.fetchone()  # station id -> ridership doesn't have station name so work with station ID

    if data_found:
        station_ID=data_found[0]
        #for Station_ID in data_found:
        #weekday ridership count
            
        print("Percentage of ridership for the" ,input2, "station: ")
        cursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = ?", (station_ID, "W"))
        weekday_riders=cursor.fetchone()[0]
       # print("  Weekday ridership: ",f"{weekday_riders:,}")

         #saturday Ridership
        cursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = ?", (station_ID, "A"))
        saturday_riders=cursor.fetchone()[0]

        #sunday/holiday ridership
        cursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = ?", (station_ID, "U"))
        holiday_riders=cursor.fetchone()[0]

        #total ridership
        cursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day IN ('U', 'A', 'W')""", (station_ID,))
        total_ridership=cursor.fetchone()[0]

        #  Weekday
        print(f"  Weekday ridership: {weekday_riders:,} ({weekday_riders / total_ridership * 100:.2f}%)")
        #  Saturday
        print(f"  Saturday ridership: {saturday_riders:,} ({saturday_riders / total_ridership * 100:.2f}%)")
        #  Sunday/Holiday
        print(f"  Sunday/holiday ridership: {holiday_riders:,} ({holiday_riders / total_ridership * 100:.2f}%)")
        print("  Total ridership:", f"{total_ridership:,}")

    else:
        print("**No data found...")

def user_input3_func():
    print("Ridership on Weekdays for Each Station")
    
    # Get the total weekday ridership across all stations
    cursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Type_of_Day = 'W'")
    total_weekday_riders = cursor.fetchone()[0]
    
    # Get the weekday ridership per station and order by ridership in descending order
    cursor.execute("""SELECT s.Station_Name, SUM(r.Num_Riders) as Weekday_Riders FROM Stations s 
    JOIN Ridership r ON s.Station_ID = r.Station_ID WHERE r.Type_of_Day = 'W' GROUP BY s.Station_Name
        ORDER BY Weekday_Riders DESC """)
    station_ridership = cursor.fetchall()
    
    # Iterate through each station, calculate the percentage, and print the result
    for station_name, weekday_riders in station_ridership:
        percentage = (weekday_riders / total_weekday_riders) * 100
        print(f"{station_name} : {weekday_riders:,} ({percentage:.2f}%)")

def user_input4_func():
    # Line color input and check if the line exists
    input_color = input("\nEnter a line color (e.g. Red or Yellow): ").strip().lower()

    # Check if the line exists by matching the color
    cursor.execute("SELECT Line_ID FROM Lines WHERE LOWER(Color) = ?", (input_color,))
    line_data = cursor.fetchone()

    if not line_data:
        print("**No such line...")
        return

    line_id = line_data[0]

    # Ask direction input and check if the direction exists for this line
    input_direction = input("Enter a direction (N/S/W/E): ").strip().upper()

    # Join the Lines and Stops table by matching Line_ID and check for direction
    cursor.execute("""
        SELECT DISTINCT s.Direction 
        FROM Stops s
        JOIN StopDetails sd ON s.Stop_ID = sd.Stop_ID
        WHERE sd.Line_ID = ? AND s.Direction = ?
    """, (line_id, input_direction))

    direction_data = cursor.fetchone()

    if not direction_data:
        print("**That line does not run in the direction chosen...")
        return

    # If both the line and direction are valid, display the stops in ascending order by name
    cursor.execute("""
        SELECT s.Stop_Name, s.ADA 
        FROM Stops s
        JOIN StopDetails sd ON s.Stop_ID = sd.Stop_ID
        WHERE sd.Line_ID = ? AND s.Direction = ?
        ORDER BY s.Stop_Name ASC
    """, (line_id, input_direction))

    stops = cursor.fetchall()

    if stops:
        #print(f"Stops for the {input_color.capitalize()} line in the {input_direction} direction:\n")
        for stop_name, ada_accessible in stops:
            ada_text = "(handicap accessible)" if ada_accessible else "(not handicap accessible)"
            print(f"{stop_name} : direction = {input_direction} {ada_text}")
    else:
        print(f"No stops found for the {input_color.capitalize()} line in the {input_direction} direction.")

# Function for command 5
# Function for command 5
def user_input5_func():
    # SQL query to fetch stop counts by line color and direction
    cursor.execute("SELECT COUNT(Stop_ID) FROM Stops;")
    total_stationN=cursor.fetchall()
    # Assuming total_stationN is fetched from the database and looks like [(302,)]
    total_stops = total_stationN[0][0]  # Extract the total number of stops
    cursor.execute("""
        SELECT 
            l.Color AS Line_Color,                   -- Line color
            s.Direction AS Direction,                -- Direction (N/S/E/W)
            COUNT(DISTINCT s.Stop_ID) AS Number_of_Stops  -- Count only distinct Stop_IDs to avoid duplicates
        FROM 
            Stops s
        JOIN 
            StopDetails sd ON s.Stop_ID = sd.Stop_ID      -- Join StopDetails on Stop_ID
        JOIN 
            Lines l ON sd.Line_ID = l.Line_ID             -- Join Lines on Line_ID
        GROUP BY 
            l.Color, s.Direction                          -- Group by Line color and Direction
        ORDER BY 
            l.Color ASC, s.Direction ASC;                 -- Order by Line color and Direction
    """)

    # Fetch the results
    results = cursor.fetchall()


    # Print the results along with percentages
    print("Number of Stops For Each Color By Direction")

    for line_color, direction, number_of_stops in results:
        percentage = (number_of_stops / total_stops) * 100  # Calculate percentage
        # Capitalize each word in the line_color, preserving the hyphen
        #capitalized_color = ' '.join(word.capitalize() for word in line_color.split('-'))
        capitalized_color = '-'.join(word.capitalize() for word in line_color.split('-'))

        print(f"{capitalized_color} going {direction} : {number_of_stops} ({percentage:.2f}%)")

#fucntion for command 6

def user_input6_func():
    station_name = input("\nEnter a station name (wildcards _ and %): ")
    
    # Query to find matching stations, using the same logic as userinput1func()
    cursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", (station_name,))
    matching_stations = cursor.fetchall()
    
    if not matching_stations:
        print("**No station found...")
        return
    elif len(matching_stations) > 1:
        print("**Multiple stations found...")
        return
    
    station_id, full_station_name = matching_stations[0]
    
    # Query to get yearly ridership
    cursor.execute("""
        SELECT strftime('%Y', Ride_Date) as Year, SUM(Num_Riders) as Total_Ridership
        FROM Ridership
        WHERE Station_ID = ?
        GROUP BY Year
        ORDER BY Year ASC
    """, (station_id,))
    
    yearly_data = cursor.fetchall()
    
    print(f"Yearly Ridership at {full_station_name}")
    years = []
    ridership = []
    for year, total in yearly_data:
        print(f"{year} : {total:,}")
        years.append(int(year))
        ridership.append(total)
    
    plot_choice = input("\nPlot? (y/n) ")
    if plot_choice.lower() == 'y':
        plt.figure(figsize=(10, 6))
        plt.plot(years, ridership, marker='o')
        plt.title(f"Yearly Ridership at {full_station_name}")
        plt.xlabel("Year")
        plt.ylabel("Total Ridership")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
#function 7
def user_input7_func():
    station_name = input("\nEnter a station name (wildcards _ and %): ")
    
    # Query to find matching stations
    cursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", (station_name,))
    matching_stations = cursor.fetchall()
    
    if not matching_stations:
        print("**No station found...")
        return
    elif len(matching_stations) > 1:
        print("**Multiple stations found...")
        return
    
    station_id, full_station_name = matching_stations[0]
    
    year = input("Enter a year: ")
    
    # Query to get monthly ridership for the specified year
    cursor.execute("""
        SELECT strftime('%m/%Y', Ride_Date) as Month, SUM(Num_Riders) as Total_Ridership
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Month
        ORDER BY Ride_Date ASC
    """, (station_id, year))
    
    monthly_data = cursor.fetchall()
    
    # If no data, print the specific message and ask for plotting
    if not monthly_data:
        print(f"Monthly Ridership at {full_station_name} for {year}")
    
    else:
        print(f"Monthly Ridership at {full_station_name} for {year}")
        months = []
        ridership = []
        for month, total in monthly_data:
            print(f"{month} : {total:,}")
            months.append(month)
            ridership.append(total)
    
    # Ask for plotting regardless of data availability
    plot_choice = input("\nPlot? (y/n) ")
    if plot_choice.lower() == 'y':
        plt.figure(figsize=(12, 6))
        if monthly_data:
            plt.bar(months, ridership)
        else:
            plt.bar([], [])  # Empty plot if no data
        plt.title(f"Monthly Ridership at {full_station_name} for {year}")
        plt.xlabel("Month")
        plt.ylabel("Total Ridership")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def user_input8_func():
    year = input("\nYear to compare against? ")

    # Get the first station name with wildcards
    station1_name = input("\nEnter station 1 (wildcards _ and %): ")
    cursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", (station1_name,))
    station1_matches = cursor.fetchall()

    if not station1_matches:
        print("**No station found...")
        return
    elif len(station1_matches) > 1:
        print("**Multiple stations found...")
        return
    station1_id, station1_full_name = station1_matches[0]

    # Get the second station name with wildcards
    station2_name = input("\nEnter station 2 (wildcards _ and %): ")
    cursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", (station2_name,))
    station2_matches = cursor.fetchall()

    if not station2_matches:
        print("**No station found...")
        return
    elif len(station2_matches) > 1:
        print("**Multiple stations found...")
        return
    station2_id, station2_full_name = station2_matches[0]

    # Fetch the ridership data for station 1 (first 5 days)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', Ride_Date), SUM(Num_Riders) 
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date ASC
        LIMIT 5
    """, (station1_id, year))
    station1_first5 = cursor.fetchall()

    # Fetch the ridership data for station 1 (last 5 days)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', Ride_Date), SUM(Num_Riders)
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date DESC
        LIMIT 5
    """, (station1_id, year))
    station1_last5 = cursor.fetchall()

    # Fetch the ridership data for station 2 (first 5 days)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', Ride_Date), SUM(Num_Riders)
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date ASC
        LIMIT 5
    """, (station2_id, year))
    station2_first5 = cursor.fetchall()

    # Fetch the ridership data for station 2 (last 5 days)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', Ride_Date), SUM(Num_Riders)
        FROM Ridership
        WHERE Station_ID = ? AND strftime('%Y', Ride_Date) = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date DESC
        LIMIT 5
    """, (station2_id, year))
    station2_last5 = cursor.fetchall()

    # Display the results for both stations
    print(f"Station 1: {station1_id} {station1_full_name}")
    for date, riders in station1_first5:
        print(f"{date} {riders}")
    for date, riders in reversed(station1_last5):
        print(f"{date} {riders}")

    print(f"Station 2: {station2_id} {station2_full_name}")
    for date, riders in station2_first5:
        print(f"{date} {riders}")
    for date, riders in reversed(station2_last5):
        print(f"{date} {riders}")

    # Plot the data if the user wants
    plot_choice = input("\nPlot? (y/n) ")
    if plot_choice.lower() == 'y':
        dates_station1 = [date for date, riders in station1_first5] + [date for date, riders in reversed(station1_last5)]
        riders_station1 = [riders for date, riders in station1_first5] + [riders for date, riders in reversed(station1_last5)]

        dates_station2 = [date for date, riders in station2_first5] + [date for date, riders in reversed(station2_last5)]
        riders_station2 = [riders for date, riders in station2_first5] + [riders for date, riders in reversed(station2_last5)]

        plt.figure(figsize=(10, 6))
        plt.plot(dates_station1, riders_station1, marker='o', label=f"{station1_full_name}")
        plt.plot(dates_station2, riders_station2, marker='o', label=f"{station2_full_name}")
        plt.title(f"Daily Ridership in {year}")
        plt.xlabel("Date")
        plt.ylabel("Total Ridership")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
    #function 9

def user_input9_func():
    # Get user input for latitude and longitude
    while True:
        try:
            lat = float(input("\nEnter a latitude: "))
            if 40 <= lat <= 43:
                break
            else:
                print("**Latitude entered is out of bounds...")
                return
        except ValueError:
            print("**Invalid input. Please enter a valid number.")

    while True:
        try:
            lon = float(input("Enter a longitude: "))
            if -88 <= lon <= -87:
                break
            else:
                print("**Longitude entered is out of bounds...")
                return
        except ValueError:
            print("**Invalid input. Please enter a valid number.")

    # Calculate bounds
    lat_lower = round(lat - (1.0 / 69.0), 3)
    lat_upper = round(lat + (1.0 / 69.0), 3)
    lon_lower = round(lon - (1.0 / (math.cos(math.radians(lat)) * 69.17)), 3)
    lon_upper = round(lon + (1.0 / (math.cos(math.radians(lat)) * 69.17)), 3)

    # Query to fetch stations within the square mile radius
    query = """
    SELECT s.Station_Name, st.Latitude, st.Longitude
    FROM Stations s
    JOIN Stops st ON s.Station_ID = st.Station_ID
    WHERE st.Latitude > ? AND st.Latitude < ? 
      AND st.Longitude > ? AND st.Longitude < ?
    GROUP BY s.Station_Name
    """
    
    cursor.execute(query, (lat_lower, lat_upper, lon_lower, lon_upper))
    
    # Process results
    nearby_stations = []
    for station in cursor.fetchall():
        if haversine_distance(lat, lon, station[1], station[2]) <= 1:
            nearby_stations.append(station)

    if not nearby_stations:
        print("**No stations found...")
    else:
        print("\nList of Stations Within a Mile")
        for station in nearby_stations:
            print(f"{station[0]} : ({station[1]:.6f}, {station[2]:.6f})")

    # Ask if user wants to plot
    plot_choice = input("\nPlot? (y/n) ")
    if plot_choice.lower() == 'y':
        plot_stations(nearby_stations, lat, lon)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3959  # Earth's radius in miles
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance

def plot_stations(stations, center_lat, center_lon):
    # Prepare data for plotting
    x = [station[2] for station in stations]  # Longitude
    y = [station[1] for station in stations]  # Latitude 
    labels = [station[0] for station in stations]

    # Load the Chicago map image
    image = plt.imread("chicago.png")
    xydims = [-87.9277, -87.5569, 41.7012, 42.0868]  # Dimensions of the map image

    # Create the plot
    plt.figure(figsize=(10, 10))
    plt.imshow(image, extent=xydims)
    plt.plot(x, y, 'ro')  # Plot stations as red dots

    # Annotate each station
    for i, label in enumerate(labels):
        plt.annotate(label, (x[i], y[i]), xytext=(5, 5), textcoords='offset points', fontsize=8)

    # Plot the center point (input coordinates)
    plt.plot(center_lon, center_lat, 'bo', markersize=10)  # Blue dot for center
    plt.annotate("Input Location", (center_lon, center_lat), xytext=(5, 5), textcoords='offset points', color='blue')

    plt.title("Stations Within a Mile")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.xlim([-87.9277, -87.5569])
    plt.ylim([41.7012, 42.0868])
    plt.show()
####################################################################

# Prompt the user for input
while True:
    user_input = input("\nPlease enter a command (1-9, x to exit): ")
   # print()
# Check if the input is 'x' for exit
    if user_input.lower() == 'x':
        break

    try:
    # Convert user input to an integer
        user_input = int(user_input)
        # Handle user command
        if user_input == 1:
            userinput1func()
        elif user_input == 2:
            userinput2func()
        elif user_input ==3:
         user_input3_func()
        elif user_input ==4:
         user_input4_func()
        elif user_input ==5:
         user_input5_func()
        elif user_input ==6:
         user_input6_func()
        elif user_input ==7:
         user_input7_func()
        elif user_input ==8:
         user_input8_func()
        elif user_input ==9:
         user_input9_func()
        else:
            print("**Error, unknown command, try again...")
    except ValueError:
            print("**Error, unknown command, try again...")

# Close the connection
conn.close()
