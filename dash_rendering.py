import logging
import MySQLdb
import pandas.io.sql as psql
import datetime
import configparser
import dash_daq as daq

class dash_rendering:
	##################################################
	# functions 

	def DatabaseAccess():
		DB=None
		if DB is None:
		    config = configparser.ConfigParser()
		    if not config.read('config.ini'):
		        logging.critical('could not open config file')
		        exit(1)
		    else:
		        try:
		            logging.info('try to establish a DB connection')
		            DB = MySQLdb.connect(host=config['DATABASE'].get('SERVER'),user=config['DATABASE'].get('USERNAME'),passwd=config['DATABASE'].get('PASSWORD'),db=config['DATABASE'].get('DATABASE'))
		            logging.info('Database Connection established')
		            return DB
		        except configparser.Error as es:
		            logging.Error('Error occured: ' + es)
		            return 1

	##################################################
	#psql.read_sql("select WEP.PLANPERFORMANCE, WEP.ISPERFORMANCE,WEP.WINDMILL, WEP.MONTH from Metabase.WIND_ENERGY_PERFORMANCE WEP where WINDMILL in (1) and YEAR in (" + yearvalue + ") order by MONTH;",dash_rendering.dash_rendering.DatabaseAccess())
	def GetLabel(query):
		logging.debug("GetLabelQuery:{0}".format(query))
		df = psql.read_sql(query,dash_rendering.DatabaseAccess())
		dataframelist = []
		for index, row in df.iterrows():
			dataframelist.append( {'label':row[0], 'value':row[1] } )
		
		logging.debug(dataframelist)
		return dataframelist

	##################################################
	def ExecuteQuery(query,name,string):
		w = "where"
		rows = query[0]["rows"]
		table = query[0]["table"]
		where = query[0]["where"]

		#check if groupby was set
		if  "groupby" in query[0]:
			groupby = " group by " + query[0]["groupby"]
		else:
			groupby = ""

		#build where clause
		for i in where:
	
			for key, value in i.items():
				if key != "Operator":
					if value != "":
						w = w + " " + i["Operator"] + " " + key  + value

		#create query
		query = "select " + rows + " from " + table + " " + w + groupby + ";"
		logging.debug("ExecuteQuery-{0}: {1}".format(name,query))
		
		if string == True:
			#return as a string
			df = psql.read_sql(query,dash_rendering.DatabaseAccess())
			logging.debug('df-{0}: {1}'.format(name,df.to_string(header=False,index=False)))

			return df.to_string(header=False,index=False)
		elif string == False:
			#return as a dataframe
			df = psql.read_sql(query,dash_rendering.DatabaseAccess())
			logging.debug('df-{0}: {1}'.format(name,df))

			return df

	##################################################
	def CheckBoxYearMonth(id,checkboxyear,checkboxmonth,rangeslideryear,rangeslidermonth,columnname):
		#columnname[0]=YEAR
		#columnname[1]=MONTH
		where = []

		if checkboxyear == ['true'] and checkboxmonth == None or not checkboxmonth:
			#if only year was chosen
			where.append({"Operator":"", id + columnname[0]:">=" + str(rangeslideryear[0])})
			where.append({"Operator":"AND", id + columnname[0]:"<=" + str(rangeslideryear[1])}) 
		elif checkboxmonth == ['true'] and checkboxyear == None or not checkboxyear:
			#if only month was chosen
			where.append({"Operator":"", id + columnname[1]:">=" + str(rangeslidermonth[0])})
			where.append({"Operator":"AND", id + columnname[1]:"<=" + str(rangeslidermonth[1])}) 
		else:
			#if month and year was chosen
			where.append({"Operator":"", id + columnname[1]:">=" + str(rangeslidermonth[0])})
			where.append({"Operator":"AND", id + columnname[1]:"<=" + str(rangeslidermonth[1])}) 
			where.append({"Operator":"AND", id + columnname[0]:">=" + str(rangeslideryear[0])})
			where.append({"Operator":"AND", id + columnname[0]:"<=" + str(rangeslideryear[1])})


		return where
				

	##################################################	
	def Windmill(Location, Windmill):
		# if a Location was picked
		if Location and Windmill is None:
			logging.debug("Location is picked")
			mill = dash_rendering.ExecuteQuery(
				[
					{
						"rows":"WM.ID",
						"table":"Metabase.WIND_MILL WM",
						"where":[
							{
								"Operator":"","WM.LOCATION":"=" + str(Location)
							}
						]
					}
				],"WINDMILL",True
			)
			mill = mill.replace("\n",",").replace(" ","")
			
		#if specific windmill was chosen from dropdown	
		elif Windmill and Location is None:
			logging.debug("Windmill is picked")
			mill = ','.join(map(str, Windmill))

			
		logging.debug("altered windmill string:{0}".format(mill))		
		return mill
		