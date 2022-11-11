import geopandas as gpd
import pandas as pd
import logging
'''
Logging setup - Screen and File Logging
'''
# Log to screen
consoleLogger = logging.getLogger('consoleLogger')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
consoleLogger.setLevel(logging.DEBUG)
consoleLogger.addHandler(handler)
# Log to app.log
fileLogger = logging.getLogger('fileLogger')
handler = logging.FileHandler('app.log')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
fileLogger.setLevel(logging.DEBUG)
fileLogger.addHandler(handler)


class surfaceScore:

    def __init__(self, geoPackage: str, scoreVal: dict, renameIndex: bool):
        self.scoreVal = scoreVal
        self.gpkg = gpd.read_file(geoPackage) 
        self.gpkg = self.gpkg.convert_dtypes()
        self.gpkg['SCORE'] = 0
        # rename index to h3_index to avoid export problems
        if renameIndex == True: self.gpkg['h3_index'] = self.gpkg['index']
        if renameIndex == True: self.gpkg = self.gpkg.drop(columns=['index'])
        consoleLogger.info(f'Successfully loaded GeoDataframe from {geoPackage}')
        fileLogger.info(f'Successfully loaded GeoDataframe from {geoPackage}')

    def addLayerToSurface(self, layerPath, fieldsToKeep: list, projCRS: int, format: str='FILE'):
        if format.upper() == 'FILE':
            self.gdfAdd = gpd.read_file(layerPath)
        else:
            self.gdfAdd = layerPath 
        fieldsToKeep.append('geometry')
        self.gdfAdd = self.gdfAdd[fieldsToKeep]
        self.gdfAdd.to_crs(epsg=projCRS, inplace=True)
        self.gpkg = gpd.sjoin(self.gpkg, self.gdfAdd, how='left', predicate='intersects')
        self.gpkg = self.gpkg.drop(['index_right'], axis=1)
        consoleLogger.info(f'Successfully joined {layerPath}') 
        fileLogger.info(f'Successfully joined {layerPath}') 

    def convertNumeric(self, field: str):
        self.gpkg[field] = pd.to_numeric(self.gpkg[field])
        self.gpkg[field] = self.gpkg[field].astype(float)

        #self.gpkg[field] = self.gpkg.astype({field: 'float32'})
        consoleLogger.info(f'{self.gpkg[field].dtype}')
        fileLogger.info(f'{self.gpkg[field].dtype}')

    def getUASrange(self, field: str):
        try:
            self.dfUAS = self.gpkg[field].str.split('|', expand=True).astype(float)
            self.gpkg = self.gpkg.assign(uasfmMAX=self.dfUAS.max(axis=1), uasfmMIN=self.dfUAS.min(axis=1))
            consoleLogger.info(f'UAS Max values: {self.gpkg["uasfmMAX"].unique()}')
            fileLogger.info(f'UAS Max values: {self.gpkg["uasfmMAX"].unique()}')
        except KeyError as e:
            consoleLogger.info(f'KeyError {e}')
            fileLogger.info(f'KeyError {e}')

    def roadScoring(self, roadsField: str, low: list, med: list, high: list):
        def roadScore(val, low, med, high):
            score, val = 0, str(val)
            score = [self.scoreVal['LOW'] for road in low if val.find(road) != -1]
            score = score[0] if len(score) else 0
            if not score:
                score = [self.scoreVal['MED'] for road in med if val.find(road) != -1]
                score = score[0] if len(score) else 0
            if not score:
                score = [self.scoreVal['HIGH'] for road in high if val.find(road) != -1]
                score = score[0] if len(score) else 0
            return score

        self.gpkg["SCORE_ROADS"] = 0
        self.gpkg['SCORE_ROADS'] = self.gpkg[roadsField].apply(roadScore, args=[low, med, high])
        consoleLogger.info(f'{self.gpkg["SCORE_ROADS"].value_counts()}')
        fileLogger.info(f'{self.gpkg["SCORE_ROADS"].value_counts()}')
    
    def lowScoreFields(self, fields: list):
        try:
            for field in fields:
                if field in self.gpkg.columns:
                    self.gpkg.loc[self.gpkg[field].notnull(), 'SCORE'] = self.scoreVal['LOW']
            consoleLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
            fileLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
        except KeyError as e:
            consoleLogger.info(f'KeyError {e}')
            fileLogger.info(f'KeyError {e}') 
    
    def medScoreFields(self, fields: list):
        try:
            for field in fields:
                if field in self.gpkg.columns:
                    self.gpkg.loc[self.gpkg[field].notnull(), 'SCORE'] = self.scoreVal['MED']
            consoleLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
            fileLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
        except KeyError as e:
            consoleLogger.info(f'KeyError {e}')
            fileLogger.info(f'KeyError {e}') 
        
    def highScoreFields(self, fields: list):
        try:
            for field in fields:
                if field in self.gpkg.columns:
                    self.gpkg.loc[self.gpkg[field].notnull(), 'SCORE'] = self.scoreVal['HIGH']
            consoleLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
            fileLogger.info(f'{self.gpkg["SCORE"].value_counts()}')
        except KeyError as e:
            consoleLogger.info(f'KeyError {e}')
            fileLogger.info(f'KeyError {e}') 
    
        
    def specialField(self, params: dict):
        try: 
            if (params['fieldType']).upper() == 'FUNC':
                self.gpkg[f'{params["newField"]}'] = self.gpkg[params["field"]].apply(params['expr'])
            elif (params['fieldType']).upper() == 'LIST':
                self.gpkg.loc[self.gpkg[params['field']].isin(params['expr']), (f'{params["newField"]}')] = params['score']
            else:
                consoleLogger.info(f'param["fTYpe"] must be ["NUM", "LIST"]')
            consoleLogger.info(f'Created new field {params["newField"]} with {params["expr"]}')
        except KeyError as e:
            consoleLogger.info(f'KeyError {e}')
            fileLogger.info(f'KeyError {e}')

    
    def exportFullSurface(self, surfaceOutput: str, outputFormat: str):
        self.surfaceOutput = surfaceOutput
        # make copy of final surface GeoDataframe
        self.expSurf = self.gpkg.copy()
        # Compare SCORE to SCORE_ROADS take highest value
        if 'SCORE_ROADS' in self.expSurf.columns:
            self.expSurf['SCORE'] = self.expSurf.apply(lambda r: r['SCORE_ROADS'] if r['SCORE_ROADS'] > r['SCORE'] else r['SCORE'], axis=1)
        # self.expSurf = self.expSurf.convert_dtypes()
        self.expSurf.to_file((self.surfaceOutput), driver=outputFormat)
        consoleLogger.info(f'Successfully saved - {self.surfaceOutput}')
        fileLogger.info(f'Successfully saved - {self.surfaceOutput}')

    def exportInsightsSurface(self, insightsOutput: str):
        self.insightsOutput = insightsOutput
        self.columns = self.gpkg.columns.tolist()
        if 'h3_index' in self.gpkg.columns:
            self.columns.remove('h3_index')
        self.columns.remove('geometry')
        self.surfMelt = pd.melt(self.gpkg, id_vars=['h3_index'], value_vars=self.columns)
        self.surfMelt = self.surfMelt.dropna(subset=['value'])
        self.surfTrim = self.gpkg[['h3_index', 'geometry', 'SCORE']]
        self.insightsSurf = self.surfMelt.merge(self.surfTrim, on='h3_index')
        self.insightsSurf.to_file((self.insightsOutput), driver='GPKG')
        consoleLogger.info(f'Successfully saved - {self.insightsOutput}')
        fileLogger.info(f'Successfully saved - {self.insightsOutput}')
