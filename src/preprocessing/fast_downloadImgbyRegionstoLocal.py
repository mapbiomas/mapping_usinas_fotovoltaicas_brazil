#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Produzido por Geodatin - Dados e Geoinformacao
DISTRIBUIDO COM GPLv2
@author: geodatin
"""
import os
import ee
import sys
import collections
import pandas as pd
import requests
import multiprocessing
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
    # "regions_on_paneis_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_08_12joins_corr",
    # "regions_on_paneis_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/buffer_5km_fotovolt_final_id",
    # "regions_on_paneis_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/buffer_5km_fotovolt_final_id",
    # "regions_on_paneis_foto": "projects/geo-data-s/assets/fotovoltaica/shp/shp_regions_grupo2_fotoVoltaica_2024_v2",
    "regions_on_paneis_foto": "projects/geo-data-s/assets/fotovoltaica/shp/shp_regions_grupo2_fotoVoltaica_2024_v2_corr",
    # "regions_on_paneis_foto": "projects/geo-data-s/assets/fotovoltaica/shp/shp_regions_grupo3_fotoVoltaica_2024_v3",
    'asset_ptos_bom_result': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/pontos_useLabel_fotovoltaicos_08_12",
    'asset_areas_erros': "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_erro_predict_fotovoltaicos_08_12",
}
################## show Planet ##########################################
# https://code.earthengine.google.com/9bbac428bc3d29d51d0cb9733efae389  #
#########################################################################

def CalculateIndiceAllinOne(imgA):    
    iiaImgY = (imgA.expression(
        "float((b('G') - 4 *  b('N')) / (b('G') + 4 *  b('N')))")
            .add(1).multiply(10000).rename(['iia']).toUint16())


    eviImgY = (imgA.expression(
        "float(2.4 * (b('N') - b('R')) / (1 + b('N') + b('R')))")
            .divide(10).add(1).multiply(10000).rename(['evi']).toUint16())

    msaviImgY = (imgA.expression(
                "float((2 * b('N') + 1 - sqrt((2 * b('N') + 1) * (2 * b('N') + 1) - 8 * (b('N') - b('R'))))/2)")
           .add(1).multiply(10000).rename(['msavi']).toUint16()
            )
    riImgY = (imgA.expression(
        "float(2.4 * (b('R') - b('G')) / (b('R') + b('G')))")
            .add(1).multiply(10000).rename(['ri']).toUint16())

    # gliImgY = imgA.expression(
    #     "float((2 * b('G') - b('R') - b('B')) / (2 * b('G') + b('R') + b('B')))")\
    #         .add(1).multiply(10000).rename(['gli']).toInt16()

    shapeImgAY = (imgA.expression(
        "float((2 * b('R') - b('G') - b('B')) / (b('G') - b('B')))")
            .divide(10).add(1).multiply(10000).rename(['shape']).toUint16())

    return imgA.toUint16().addBands(iiaImgY).addBands(eviImgY).addBands(
                    riImgY).addBands(msaviImgY).addBands(shapeImgAY)


def CalculateIndiceAllinOneOld(imgA):    
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

# rutaOutpatches = '/home/superuser/Dados/mapbiomas/mapping_areas_eolicas_fotovoltaicas/src/dados/patchs_FV'
# path_folder = '/home/superuser/Dados/mapbiomas/mapping_areas_eolicas_fotovoltaicas/src/dados/array_tif'
path_folder = '/home/superuser/Dados/mapbiomas/mapping_areas_eolicas_fotovoltaicas/src/dados/array_tif_g2'
nshp_regionsFoto  = ee.FeatureCollection(param['regions_on_paneis_foto'])
nshp_regionsFoto = nshp_regionsFoto.map(lambda feat: feat.set('idCod', feat.id()))
print(nshp_regionsFoto.first().getInfo()['id'])
lstIdregions = nshp_regionsFoto.reduceColumns(ee.Reducer.toList(), ['system:index']).get('list').getInfo()
print(f" we have to collecting in {len(lstIdregions)} regions ")
print(lstIdregions[:2])


lstDownlImgErrors = [ "0000000000000000001b"]
# lstDownlImgErrors = []

# @retry(tries=10, delay=1, backoff=2)
def getResult(cont, cod_name_exp):
    
    """Handle the HTTP requests to download an image."""
    print("entrando ao threadss ", cod_name_exp)
    bandasInt = ['B', 'G', 'R', 'N', 'iia', 'evi', 'ri', 'msavi', 'shape']
    partes = cod_name_exp.split("_")
    idCod = partes[0]
    yyear = int(partes[1])
    month = int(partes[2])
    if yyear != 2025:
        date_init = ee.Date.fromYMD(yyear, month, 1)
        date_end = date_init.advance(1, 'month')
    else:
        date_init = ee.Date.fromYMD(yyear, 2, 1)
        date_end = date_init.advance(1, 'month')

    nshpRegionsFoto  = (ee.FeatureCollection(param['regions_on_paneis_foto'])
                            .filter(ee.Filter.eq('system:index', idCod)))

    print("Quantidade de grades ", nshpRegionsFoto.size().getInfo())  # 
    nshpRegionsFoto = nshpRegionsFoto.geometry()    

    base_biomas = ee.Image(param['asset_biomas_raster']).gt(0)
    # https://code.earthengine.google.com/5a8ae11fd31afcc9da09e29a1a0a0ae0x
    imgMosPlanet = ee.ImageCollection(param['assetNICFI'])
    # print("ver quantidade de image planet ", imgMosPlanet.size().getInfo())
    try:
        if int(yyear) < 2020:
            print("mosaico semestral")
            imgMosPlanet = imgMosPlanet.map(lambda img: img.set(
                                                'year', ee.Number(ee.Date(img.get("system:time_start")).get('year')),
                                                'month', ee.Number(ee.Date(img.get("system:time_start")).get('month'))
                                        )
                          )
            # print(imgMosPlanet.first().getInfo())
            imgPlanet = imgMosPlanet.filter(
                            ee.Filter.And(
                                        ee.Filter.eq("year", int(yyear)), 
                                        ee.Filter.eq("month", 12) )
                                ).first()
        else:
            imgPlanet = imgMosPlanet.filter(ee.Filter.date(date_init, date_end)).first()

        imgPlanet =  ee.Image(imgPlanet).updateMask(base_biomas)
        print("number the imagens loading ", imgPlanet.bandNames().getInfo())
        tmpImgPlanet = imgPlanet.clip(nshpRegionsFoto)
        imgMosaicNorm = CalculateIndiceAllinOne(tmpImgPlanet)
        print(imgMosaicNorm.bandNames().getInfo())
        exportImage_viaURL(imgMosaicNorm, f"reg_{cod_name_exp}.tif", nshpRegionsFoto, bandasInt)

    except :
        print("============= fails ", cod_name_exp, " =================")
        try:
            processoExportar(imgMosaicNorm,nshpRegionsFoto, f"reg_{cod_name_exp}")
        except:
            print("============= imagem  ", cod_name_exp, " não existe =================")
    
def exportImage_viaURL(imgBuild, nameImg, mgeomRect, bnd_mosaic):    
    pathExp = os.path.join(path_folder , nameImg)
    # Fetch the URL from which to download the image.
    # Multi-band GeoTIFF file.
    download_idV = ee.data.getDownloadId({
        'image': imgBuild,
        'bands': bnd_mosaic,
        'region': mgeomRect,
        'scale': 5,
        'csr':  "EPSG:3857",
        'format': 'GEO_TIFF'
    })
    response = requests.get(ee.data.makeDownloadUrl(download_idV))
    with open(pathExp, 'wb') as fd:
        fd.write(response.content)
    print("Done: ", nameImg)

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


lstPathImgSaved = os.listdir(path_folder)
print(f"have saved {len(lstPathImgSaved)} img tif")
print(lstPathImgSaved[:5])
month = 10
# sys.exit()
lstIDyyReg = []
for year in range(2015, 2026): 
    lstMeses = [10] #[6, 9, 10, 11]
    # if year != 2024:
    if year == 2025:
        lstMeses = [10]
    for month in lstMeses:
        for cc, idreg in enumerate(lstIdregions[:]):
            print(f" # {cc} adding to list  >> id polygons >> {idreg} >> year {year}")
            idImg = f"reg_{idreg}_{year}_{month}.tif"
            if idImg not in lstPathImgSaved:
                # if idreg == "0000000000000000001b":
                print(" adding ... ")
                lstIDyyReg.append(f"{idreg}_{year}_{month}")

print(f"we will have process {len(lstIDyyReg)} img tif")
# sys.exit()
print(f"========= exporting {len(lstIDyyReg)} process ================================")
pool = multiprocessing.Pool(5)
pool.starmap(getResult, enumerate(lstIDyyReg[:]))
