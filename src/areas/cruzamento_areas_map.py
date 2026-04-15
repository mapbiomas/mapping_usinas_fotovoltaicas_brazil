#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
# SCRIPT DE CLASSIFICACAO POR BACIA
# Produzido por Geodatin - Dados e Geoinformacao
# DISTRIBUIDO COM GPLv2
'''

import ee 
import sys
import glob
import copy
import collections
collections.Callable = collections.abc.Callable

##############################################
###     Helper function
###    @param item 
##############################################
def convert2featCollection (item):
    item = ee.Dictionary(item)
    feature = ee.Feature(ee.Geometry.Point([0, 0])).set(
        'classe', item.get('classe'),"area", item.get('sum'))
        
    return feature

#########################################################################
####     Calculate area crossing a cover map (deforestation, mapbiomas)
####     and a region map (states, biomes, municipalites)
####      @param image 
####      @param geometry
#########################################################################
# https://code.earthengine.google.com/5a7c4eaa2e44f77e79f286e030e94695
def calculateArea (image, pixelArea, reg_geom):

    pixelArea = pixelArea.addBands(image.rename('classe'))
    reducer = ee.Reducer.sum().group(1, 'classe')
    optRed = {
        'reducer': reducer,
        'geometry': reg_geom,
        'scale': 30,
        'bestEffort': True, 
        'maxPixels': 1e13
    }    
    areas = pixelArea.reduceRegion(**optRed)

    areas = ee.List(areas.get('groups')).map(lambda item: convert2featCollection(item))
    areas = ee.FeatureCollection(areas)    
    return areas

def iterandoXanoImCruda(imgsMapp, regImg, regCod):
    pixelArea = ee.Image.pixelArea().divide(10000).clip(regImg)
     
    mapBS2rec = ee.Image(params['asset_colection_sentinel']).clip(regImg)
    areaGeral = ee.FeatureCollection([]) 
    for nyear in range(2015, 2025):
        # para cada ano  
        print("processing year >> ", nyear)
        band_select = 'classification_' + str(nyear)  
        if nyear == 2024:
            band_select = 'classification_2023'
        if nyear == 2015:
            band_select = 'classification_2016'
        
        imgMapYY = imgsMapp.filter(ee.Filter.eq('year', nyear)).first()   
        # print(imgMapYY.getInfo())   
        rasterClass = mapBS2rec.select(band_select).updateMask(imgMapYY)
        
        areaTemp = calculateArea (rasterClass, pixelArea, regImg)        
        areaTemp = areaTemp.map( lambda feat: feat.set(
                                            'year', nyear, 
                                            'código',str(regCod)
                                        ))
        areaGeral = areaGeral.merge(areaTemp)
    return areaGeral


def processoExportar(areaFeat, nameT):      
    optExp = {
          'collection': areaFeat, 
          'description': nameT, 
          'folder': 'FV_filtersXClass'        
        }    
    task = ee.batch.Export.table.toDrive(**optExp)
    task.start() 
    print("salvando ... " + nameT + "..!")   


try:
    ee.Initialize(project= 'geo-data-s')    
    # ee.Initialize(project= 'mapbiomas-caatinga-cloud05')
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

params = {
    'asset_Col9' : "projects/mapbiomas-public/assets/brazil/lulc/collection9/mapbiomas_collection90_integration_v1",
    'asset_fotovol_predC' : 'projects/geo-data-s/assets/fotovoltaica/version_2_clean',      
    #'asset_colection_sentinel': 'projects/mapbiomas-public/assets/brazil/lulc/collection_S2_beta/collection_LULC_S2_beta'
    'asset_colection_sentinel': 'projects/mapbiomas-public/assets/brazil/lulc_10m/collection2/mapbiomas_10m_collection2_integration_v1'
}


fotovol_predCle = ee.ImageCollection(params['asset_fotovol_predC']);
lstCod = fotovol_predCle.reduceColumns(ee.Reducer.toList(), ['idCod']).get('list')
lstCod = ee.List(lstCod).distinct().getInfo()
for cc, ncod in enumerate(lstCod[:]):
    print(f"#{cc}  processing >> {ncod} <<")
    rasters_tmp = fotovol_predCle.filter(ee.Filter.eq('idCod', ncod))
    # print("show metadata ", raster_tmp.get('system:index').getInfo())
    reg_raster = rasters_tmp.first().geometry()
    area_region = iterandoXanoImCruda(rasters_tmp, reg_raster, ncod)
    processoExportar(area_region, ncod + "_update")

