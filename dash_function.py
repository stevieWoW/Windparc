import logging
import MySQLdb
import pandas.io.sql as psql
import datetime
import configparser
import pandas as pd
import numpy as np
import dash_daq as daq

class dash_function:
	##################################################
	# functions 

	def DatabaseAccess():
		DB=None
		if DB is None:
		    config = configparser.ConfigParser()
		    if not config.read('/var/www/html/Dash/assets/config.ini'):
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
	#psql.read_sql("select WEP.PLANPERFORMANCE, WEP.ISPERFORMANCE,WEP.WINDMILL, WEP.MONTH from Metabase.WIND_ENERGY_PERFORMANCE WEP where WINDMILL in (1) and YEAR in (" + yearvalue + ") order by MONTH;",dash_function.dash_function.DatabaseAccess())
	def GetLabel(query):
		logging.debug("GetLabelQuery:{0}".format(query))
		df = psql.read_sql(query,dash_function.DatabaseAccess())
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
		if "where" in query[0]:
			where = query[0]["where"]
			#build where clause
			for i in where:
		
				for key, value in i.items():
					if key != "Operator":
						if value != "":
							w = w + " " + i["Operator"] + " " + key  + value
		else:
			w=""


		#check if groupby was set
		if  "groupby" in query[0]:
			groupby = " group by " + query[0]["groupby"]
		else:
			groupby = ""

		#create query
		query = "select " + rows + " from " + table + " " + w + groupby + ";"
		logging.debug("ExecuteQuery-{0}: {1}".format(name,query))
		
		if string == True:
			#return as a string
			df = psql.read_sql(query,dash_function.DatabaseAccess())
			logging.debug('df-{0}: {1}'.format(name,df.to_string(header=False,index=False)))

			return df.to_string(header=False,index=False)
		elif string == False:
			#return as a dataframe
			df = psql.read_sql(query,dash_function.DatabaseAccess())
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
			mill = dash_function.ExecuteQuery(
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

	def GetMinMonthWithoutPerf():
		#get month to start prediction with
		mm = dash_function.ExecuteQuery(
                [
                    {
                        "rows":"DISTINCT WEP.MONTH",
                        "table":"Metabase.WIND_ENERGY_PERFORMANCE WEP",
                        "where":[
							{"Operator":"","WEP.ISPERFORMANCE":" IS NULL"},
							{"Operator":"AND","WEP.YEAR = ":str(datetime.datetime.today().year)}
						]
                    }
                ],"MonthStartPrediction",False
            )
		return mm.min()["MONTH"]


	def GetMedian(df,aggregation,mill,monthtopredict):
		logging.debug('df: {}'.format(df))
		logging.debug('Aggregation: {}'.format(aggregation))
		logging.debug('mill {}'.format(mill))
		logging.debug('monthtopredict: {}'.format(monthtopredict))
		
		#if it is type set, convert to list
		if isinstance(monthtopredict, set):
			monthtopredict = list(monthtopredict)

		#standard where clause
		wherepredict = [
			{"Operator":"","WEP.MONTH":" IN(" + ','.join(map(str, monthtopredict)) +")" },
			{"Operator":"AND","WEP.YEAR":"<>" + str(datetime.datetime.today().year) }
		]

		#if specific windmill was picked append a new where condition
		if mill:
			wherepredict.append({"Operator":"AND","WEP.WINDMILL":" IN(" + mill + ")"})

		if aggregation=="WINDMILL":
			rows="sum(WEP.ISPERFORMANCE) as _IS, WEP.WINDMILL,WEP.MONTH,WEP.YEAR"
			groupby="WEP.WINDMILL,WEP.MONTH,WEP.YEAR order by WEP.WINDMILL"
			
		else:
			rows="sum(WEP.ISPERFORMANCE) as _IS, WEP.MONTH, WEP.YEAR"
			groupby="WEP.MONTH,WEP.YEAR"
			
		# get the data to predict with 
		dfpred = dash_function.ExecuteQuery(
			[
				{
					"rows":rows,
					"table":"Metabase.WIND_ENERGY_PERFORMANCE WEP",
					"where":wherepredict,
					"groupby":groupby
				}
			],"PredictionDataframe",False
		)
		

		
		

		if aggregation == "MONTH":
			#monthly prediction
			
			#get the median by month
			dfmedian = dfpred[['MONTH','_IS']].groupby('MONTH').median()
			
			#new dataframe with prediction data. 
			#adds median of previous years to numbers of this year months to predict. 
			#fillnan() is required if only current year was picked and these _IS Values are NaN
			#set_index() to match the correct values
			#between() to pick the correct months
			dfpredicted = dfmedian + df[['MONTH','_IS']][df['MONTH'].between(monthtopredict[:1][0],monthtopredict[-1:][0])].set_index('MONTH').fillna(0)
			logging.debug("median per month: {0}".format(dfmedian))
			logging.debug("df month in between: {0}".format(df[['MONTH','_IS']][df['MONTH'].between(monthtopredict[:1][0],monthtopredict[-1:][0])].set_index('MONTH').fillna(0)))
			logging.debug("return dfpredicted(df + df month in between): {0}".format(dfpredicted.reset_index()))
			return dfpredicted.reset_index()

		elif aggregation == "YEAR":
			#yearly prediction

			#get the median by month
			dfmedian = dfpred[['MONTH','_IS']].groupby('MONTH').median()

			# sum medians of remaining months and add that number to the number produced until now
			# only affects the current year
			df.loc[df.YEAR == datetime.datetime.today().year, '_IS']= df.loc[df['YEAR'] == datetime.datetime.today().year]['_IS'] + dfmedian['_IS'].sum().item()
			# return only current year, which by default is the last row
			logging.debug("return df.iloc[-1:]: {0}".format(df.iloc[-1:]))
			return df.iloc[-1:]

		elif aggregation == "WINDMILL":
			#get the median by month,windmill
			dfmedian = dfpred[['MONTH','_IS','WINDMILL']].groupby(['MONTH','WINDMILL']).median()
			logging.debug("median per month,windmill: {0}".format(dfmedian))
			logging.debug("df windmill(produced): {0}".format(df[['WINDMILL','_IS']].set_index('WINDMILL').fillna(0)))
			#sum produced values with predicted
			dfwindmill = dfmedian.groupby(['WINDMILL']).sum() + df[['WINDMILL','_IS']].set_index('WINDMILL').fillna(0)
			logging.debug("windmill prediction: {0}".format(dfwindmill.reset_index()))

			return dfwindmill.reset_index()
		