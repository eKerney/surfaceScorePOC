from scoring import surfaceScore

surfaceNames = ['WHITMORE LAKE', 'YPSILANTI', 'WEST WILLOW', 'AUGUSTA TOWNSHIP', 'SYCAMORE MEADOWS']

for surface in surfaceNames:
    geoPackage = (f'./../data/{surface}{outSuffix}.gpkg')
    surfScor = surfaceScore(geoPackage, {'LOW': 5, 'MED': 50, 'HIGH': 200}, renameIndex=True)

    layerPath1 = 'C:\\Users\\Eric Kerney\\Documents\\ArcGIS\\Projects\\MI_DOE\\OSM_High_sel.shp'
    surfScor.addLayerToSurface(layerPath1, ['highway'], 4326)
    layerPath2 = 'C:\\Users\\Eric Kerney\\Documents\\ArcGIS\\Projects\\MI_DOE\\washtenawRail.shp'
    surfScor.addLayerToSurface(layerPath2, ['FRA_ID'], 4326)

    field = 'population_density'
    surfScor.convertNumeric(field)
    field = 'uasfm_ceiling_CEILING'
    surfScor.getUASrange(field)

    surfScor.roadScoring(roadsField='highway',
        low=["residential", "unclassified", "service", "track"], 
        med=["secondary", "tertiary", "secondary_link", "tertiary_link", "road"], 
        high=["motorway", "trunk", "primary", "motorway_link", "trunk_link", "primary_link", "living_street", "pedestrian", "footway", "bridleway", "steps", "path", "cycleway", "crossing"])

    lowFields = ['transmission_lines_objectid']
    surfScor.lowScoreFields(lowFields)

    medFields = ['FRA_ID']
    surfScor.medScoreFields(medFields)

    highFields = ['schools_objectid', 'airports_IDENT', 'hospitals_objectid', 'prisons_objectid', 
        'fcc_asr_objectid', 'helipads_objectid', 'electric_substations_objectid', 
        'police_stations_objectid', 'eocs_objectid', 'wind_farms_objectid', 
        'faa_obstacles_objectid', 'military_facilities_objectid', 'power_plants_objectid' ]
    surfScor.highScoreFields(highFields)

    params = {'field': 'population_density', 'fType': 'NUM', 'expr': '> 350', 'score': 200}
    surfScor.specialFieldScore(params)
    lulc_list = ["Developed High Intensity","Developed, Medium Intensity", "Developed, Low Intensity"]
    params = {'field': 'lulc_mode', 'fType': 'LIST', 'expr': lulc_list, 'score': 200}
    surfScor.specialFieldScore(params)
    lulc_list = ["Developed High Intensity","Developed, Medium Intensity", "Developed, Low Intensity"]
    params = {'field': 'lulc_mode', 'fType': 'LIST', 'expr': lulc_list, 'score': 200, 'newField': 'LULC_Hazard'}
    surfScor.derivedField(params)
    params = {'field': 'population_density', 'fType': 'NUM', 'expr': '> 350', 'score': 200, 'newField': 'Pop_greaterthan0'}
    surfScor.derivedField(params)

    surfScor.exportFullSurface(f'./../scoring/scoreData/{surface}_{outSuffix}', 'Shapefile'

