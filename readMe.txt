Commands:

#Creating Table (please run all these table commands in order to test the further commands)
produce table SignalData with columns: Timestamp datetime, Frequency int, SignalStrength int, Modulation string, Bandwidth int, DeviceType string, AntennaType string

produce table Weather with columns: Timestamp datetime, Temperature int, Humidity int, WindSpeed int, Precipitation float, WeatherCondition string

produce table Status with columns: Timestamp datetime, InterferenceType string, CPUUsage int, MemoryUsage float, WiFiStrength int, DiskUsage float, SystemLoad float, DeviceStatus string

produce table IQData with columns: Timestamp datetime, DeviceType string, IQData list

#Insertion
include a new entry in Weather with Timestamp == 6/5/23 09:00, Temperature == 35, Humidity == 40, WindSpeed == 23, Precipitation == 0, WeatherCondition == Sunny

#Updating
edit InterferenceType to NA where InterferenceType == 'None' in Status

#Deletion
eliminate from Weather where Precipitation == '0'
eliminate from Weather where WeatherCondition == 'Sunny'

#Projection
display Humidity, Precipitation from Weather
display AntennaType, DeviceType from SignalData
display all from IQData

#Filtering
give the entries from Weather where WindSpeed > 10
give the entries from Weather where WeatherCondition == 'Rainy'

#Ordering
arrange the data in IQData by DeviceType with ascending order

#Join
combine SignalData and IQData using DeviceType with inner
combine SignalData and IQData using DeviceType with left
combine SignalData and IQData using DeviceType with right
combine SignalData and IQData using DeviceType with cross

#Aggregation
compute Temperature, Humidity from Weather using sum
compute Temperature, Humidity from Weather using avg
compute Temperature, Humidity from Weather using count
compute Temperature, Humidity from Weather using min
compute Temperature, Humidity from Weather using max

#Grouping
group WeatherCondition from Weather with Humidity using sum


Steps to run the code:
In the code, the paths for the Dataset, Chunks folder and Tables folder need to be changed according to the system it is going to be tested on. (Lines: 45, 48, 87, 540, 544)

To run the code, one can use the Terminal (MAC) or the VSCode Terminal and run it by the following syntax:

python Final.py

or

python3 Final.py

(my VSCode runs with the first command, but if your environment runs with the latter, please use that.)
(Terminal on MAC works for both the commands for me.)
(incase prettytable doesn’t work, please run pip install prettytable)

I have tested the code on a macOS.

TO EXIT THE CLI, please type exit.