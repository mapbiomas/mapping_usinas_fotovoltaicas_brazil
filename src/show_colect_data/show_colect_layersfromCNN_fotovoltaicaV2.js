var vis = {
    planet: {
        'min':14,
        'max':3454,
        'bands': ['R','G','B']
    },
    clusters: {
        min: 0, max: 1,
        palette: ["#600504","#d5e68d"]
    },
    clustersV1: {
        min: 0, max: 1,
        palette: ["#600504","#d4bc0d"]
    },
    regiones: {color: '#ece22f'},
    poligonosFV : { color: '#9d3bca'}
};
// === scripts com poligonos feitos 
// https://code.earthengine.google.com/5f243cd97de0ac2aadff70e4b8ff2997
var param = {
    'asset_fotovol_predv2' : 'projects/geo-data-s/assets/fotovoltaica/version_2',
    'asset_fotovol_predv1' : 'projects/geo-data-s/assets/fotovoltaica/versao1',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    "asset_polygons_FotoV": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/polygons_base_paneis_fotovoltaicos_19_11',
    "asset_regions_FotoV": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_19_11',
    'asset_output_Polygons': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',    
}


function processoExportar(ROIsFeat, nameB, idAsset){
    var assetIdss =  idAsset + '/' + nameB;
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetIdss          
        }
    Export.table.toAsset(optExp) 
    print("salvando ... " + nameB + "..!")    
}

//===========================================//
var numbPol = 130; // ver emprendimento das 130 regions  desenhar 17, e 57
//==========================================//
var bioCaat = ee.Image(param.asset_biomas_raster).gt(0);//.eq(5)
var lstFailVector = [
    '0000000000000000000e_pred_v2', '00000000000000000023_pred_v2',
    '00000000000000000050_pred_v2', '00000000000000000062_pred_v2'
]
                  
// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
// Filter basemaps by date and get the first image from filtered results
var basemapPlanet = nicfi.filter(ee.Filter.date('2024-10-01','2024-11-20')).first();
basemapPlanet = basemapPlanet.updateMask(bioCaat);             

var polygonFotov = ee.FeatureCollection(param.asset_polygons_FotoV);
print(" we have loaded fotovoltaica polygons with ", polygonFotov.size());
print(" Polygon Fotovoltaica ", polygonFotov.first());
var regionsFotoV = ee.FeatureCollection(param.asset_regions_FotoV);
print(" regionms rectagular fotovoltaicas ", regionsFotoV.size());
var fotovol_predv2 = ee.ImageCollection(param.asset_fotovol_predv2)
                        .map(function (img) { return img.toByte() });
                          
var regFVselect = fotovol_predv2.filter(ee.Filter.eq('system:index', lstFailVector[0]))
fotovol_predv2 = fotovol_predv2.max().selfMask();
                          
var fotovol_predv1 = ee.ImageCollection(param.asset_fotovol_predv1)
                          .map(function(img){return img.toByte()}).max().selfMask();

var regSelect = regionsFotoV.toList(131);
regSelect = ee.List(regSelect);
Map.addLayer(basemapPlanet, vis.planet, 'planet geral', false);
Map.addLayer(polygonFotov, vis.poligonosFV, 'polygons FotoVolt', false);
Map.addLayer(fotovol_predv2, vis.clusters, 'fotoVolt predv2');
Map.addLayer(fotovol_predv1, vis.clustersV1, 'fotoVolt predv1', false);
Map.addLayer(regionsFotoV, vis.regiones, 'region FotoVolt', false);
// Map.centerObject(ee.Feature(regSelect.get(numbPol)), 16);
Map.centerObject(regFVselect.first(), 16);
Map.setOptions("SATELLITE");


var nameExports = 'regions_erro_predict_fotovoltaicos_18_12';
processoExportar(region_errors, nameExports, param.asset_output_Polygons);