#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import os
import ee
import copy
import sys
import collections
import pandas as pd
pd.set_option("mode.copy_on_write", True)
from pathlib import Path
collections.Callable = collections.abc.Callable

pathparent = str(Path(os.getcwd()).parents[0])
sys.path.append(pathparent)
from configure_account_projects_ee import get_current_account, get_project_from_account
from gee_tools import *
projAccount = get_current_account()
print(f"projetos selecionado >>> {projAccount} <<<")

try:
    ee.Initialize(project= projAccount) # project='ee-cartassol'  #  'geo-data-s' # 'mapbiomas-caatinga-cloud02'
    print('The Earth Engine package initialized successfully!')
except ee.EEException as e:
    print('The Earth Engine package failed to initialize!')
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


makeDict = False
param = {
    'asset_eolica' : 'projects/mapbiomas-arida/eol_existente',
    'aaset_fotovol': 'projects/mapbiomas-arida/ufv_existente',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    "asset_output_raster": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/rotulos',
    "asset_output_shp": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',
    'asset_fotovol_pred' : 'projects/geo-data-s/assets/fotovoltaica/versao1',  # resultado primeira versão 
    "regions_regRect_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos",
    "regions_paneis_foto": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/polygons_base_paneis_fotovoltaicos_08_12',
    "regions_on_paneis_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_08_12joins_corr",
    'asset_ptos_bom_result': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/pontos_useLabel_fotovoltaicos_08_12",
    'asset_areas_erros': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_erro_predict_fotovoltaicos_08_12",
}
################## show Planet ##########################################
# https://code.earthengine.google.com/9bbac428bc3d29d51d0cb9733efae389  #
#########################################################################

def CalculateIndiceAllinOne(imgA):    
    iiaImgY = imgA.expression(
        "float((b('G') - 4 *  b('N')) / (b('G') + 4 *  b('N')))")\
            .add(1).multiply(10000).rename(['iia']).toInt16()


    eviImgY = imgA.expression(
        "float(2.4 * (b('N') - b('R')) / (1 + b('N') + b('R')))")\
            .add(1).multiply(10000).rename(['evi']).toInt16()

    riImgY = imgA.expression(
        "float(2.4 * (b('R') - b('G')) / (b('R') + b('G')))")\
            .add(1).multiply(10000).rename(['ri']).toInt16()

    gliImgY = imgA.expression(
        "float((2 * b('G') - b('R') - b('B')) / (2 * b('G') + b('R') + b('B')))")\
            .add(1).multiply(10000).rename(['gli']).toInt16()

    shapeImgAY = imgA.expression(
        "float((2 * b('R') - b('G') - b('B')) / (b('G') - b('B')))")\
            .add(10000).rename(['shape']).toInt16()

    return imgA.toInt16().addBands(iiaImgY).addBands(eviImgY).addBands(
                    riImgY).addBands(gliImgY).addBands(shapeImgAY)


#exporta a imagem classificada para o asset
def processoExportar(patches, regionB, nomeDesc):

    optExp = {
        'image': patches, 
        'description': nomeDesc, 
        'folder': 'patchesTif_FotoVv3', 
        'fileNamePrefix': nomeDesc, 
        'region':regionB.getInfo()['coordinates'], #['coordinates']
        'scale': 4, 
        'maxPixels': 1e13,
    }
    task = ee.batch.Export.image.toDrive(**optExp)
    task.start() 
    print(" ▶️ salvando ... " + nomeDesc + "..!")
    # print(task.status())



yyear = 2015
base_biomas = ee.Image(param['asset_biomas_raster']).gt(0)
imgMosPlanet = ee.ImageCollection(param['assetNICFI'])
print("ver quantidade de image planet ", imgMosPlanet.size().getInfo())

imgPlanet = imgMosPlanet.filter(ee.Filter.date(f'{yyear}-10-01',f'{yyear}-12-31')).first()
imgPlanet =  ee.Image(imgPlanet).updateMask(base_biomas);
print("number the imagens loading ", imgPlanet.bandNames().getInfo())

nshp_baseFoto  = ee.FeatureCollection(param['regions_paneis_foto']);
print(f" we have to collecting polygons in {nshp_baseFoto.size().getInfo()} regions ")

nshp_regionsFoto  = ee.FeatureCollection(param['regions_on_paneis_foto']);
lstIdregions = nshp_regionsFoto.reduceColumns(ee.Reducer.toList(), ['idCod']).get('list').getInfo();
print(f" we have to collecting in {len(lstIdregions)} regions ");

# carregar o resultado da versão anterior 
shp_ptosLabelV1 = ee.FeatureCollection(param['asset_ptos_bom_result']);
print(f" we have {shp_ptosLabelV1.size().getInfo()} points with regions e good classified");

fotovol_pred = ee.ImageCollection(param['asset_fotovol_pred']).map( 
                            lambda img: img.toByte())  #.max().selfMask();

nshp_regionsErros  = ee.FeatureCollection(param['asset_areas_erros']);
print(f" we have to {nshp_regionsErros.size().getInfo()} regions with erros ");

lstDownlImgErrors = [
    "00000000000000000072","00000000000000000068","00000000000000000059",
    "00000000000000000055","0000000000000000004e","0000000000000000004d",
    "0000000000000000004b","00000000000000000046","00000000000000000041",
    "0000000000000000003d","0000000000000000003c","00000000000000000037",
    "00000000000000000036","00000000000000000034","00000000000000000033",
    "00000000000000000032","0000000000000000002e","00000000000000000028",
    "00000000000000000026","00000000000000000020","0000000000000000001a",
    "00000000000000000013"
]

for cc, idreg in enumerate(lstIdregions[:]):
    print(f" # {cc}  >> id polygons >> {idreg}")
    # if idreg in lstDownlImgErrors:
    feattmp = nshp_regionsFoto.filter(ee.Filter.eq('idCod', idreg))
    tmpImgPlanet = imgPlanet.clip(feattmp.geometry())
    imgMosaicNorm = CalculateIndiceAllinOne(tmpImgPlanet)
    featpol = nshp_baseFoto.filterBounds(feattmp.geometry())
    featPtosB = shp_ptosLabelV1.filterBounds(feattmp.geometry())
    featErros = nshp_regionsErros.filterBounds(feattmp.geometry())
    numPoly = featpol.size().getInfo()
    numPtos = featPtosB.size().getInfo()
    numShpErros = featErros.size().getInfo()

    nLabelMap = ee.Image.constant(0).toInt16().rename('class')
    
    if numPoly > 0:
        label_map = featpol.reduceToImage(['class'], ee.Reducer.first()).unmask(0).toInt16().rename('class');
        label_map = label_map.clip(feattmp.geometry())
        nLabelMap = nLabelMap.add(label_map.unmask(0))
    
    if numPtos > 0:
        label_map = fotovol_pred.filterBounds(feattmp.geometry()).max().unmask(0).clip(feattmp.geometry())
        if numShpErros > 0:
            featErros = featErros.map(lambda feat: feat.set('etiqueta', 1))
            label_mapErr = featErros.reduceToImage(['etiqueta'], ee.Reducer.first()).unmask(0).toInt16().rename('etiqueta');
            label_mapErr = label_mapErr.clip(feattmp.geometry())
            label_map = label_map.where(label_mapErr.eq(1), 0)
        label_map = label_map.toInt16().rename('class')
        nLabelMap = nLabelMap.add(label_map.unmask(0)).gt(0)
        
    nLabelMap = nLabelMap.clip(feattmp.geometry()).rename('class');
    imgMosaicNorm = imgMosaicNorm.addBands(label_map)

    bandsMosaicsYears = imgMosaicNorm.bandNames().getInfo()
    print('lista de bandas \n ', bandsMosaicsYears)
    # break
    processoExportar(imgMosaicNorm, feattmp.geometry(), f"{idreg}_{yyear}")