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
    regiones: {color: '#ece22f'},
    poligonosFV : { color: '#9d3bca'}
};
// === scripts com poligonos feitos 
// https://code.earthengine.google.com/b4b7c5d9eb8554d73f4196e596935b90
var param = {
    'asset_fotovol_pred' : 'projects/geo-data-s/assets/fotovoltaica/version_2_clean',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    "asset_polygons_FotoV": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/polygons_base_paneis_fotovoltaicos_19_11',
    "asset_regions_FotoV": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_19_11',
    'asset_output_Polygons_FotoV': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',
    'asset_output_regions_FotoV': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',
    'asset_estados': 'projects/mapbiomas-workspace/AUXILIAR/estados-2017',
    'asset_municipios': 'projects/mapbiomas-workspace/AUXILIAR/municipios-2020'
}


function processoExportar(ROIsFeat, nameB){
    var assetIdss =  param.asset_output_shp + '/' + nameB;
    var optExp = {
          'collection': ROIsFeat, 
          'description': nameB, 
          'assetId': assetIdss          
        }
    Export.table.toAsset(optExp) 
    print("salvando ... " + nameB + "..!")    
}

//===========================================//
var numbPol = 9; // ver emprendimento das 130 regions  desenhar 17, e 57
//==========================================//
var bioCaat = ee.Image(param.asset_biomas_raster).gt(0);//.eq(5)
                  
// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
// Filter basemaps by date and get the first image from filtered results
var basemapPlanet = nicfi.filter(ee.Filter.date('2024-10-01','2024-11-20')).first();
basemapPlanet = basemapPlanet.updateMask(bioCaat);             

var polygonFotov = ee.FeatureCollection(param.asset_polygons_FotoV);
print(" we have loaded fotovolt polygons with ", polygonFotov.size());
print(polygonFotov.first())
var regionsFotoV = ee.FeatureCollection(param.asset_regions_FotoV);
print(" regionms rectagular fotovoltaicas ", regionsFotoV.size());

var fotovol_pred = ee.ImageCollection(param['asset_fotovol_pred'])
                        .filter(ee.Filter.eq('year', 2024))
                        .map(function(img){return img.toByte()});                        
print("show layer fotovoltaicas ", fotovol_pred);
fotovol_pred = fotovol_pred.max().selfMask();
var shpEstados = ee.FeatureCollection(param.asset_estados);
print('show metadata of shape States ', shpEstados);
var shpMun = ee.FeatureCollection(param.asset_municipios);
print('show metadata of shape Municipios ', shpMun);

var regSelect = regionsFotoV.toList(131);
regSelect = ee.List(regSelect)

var outline_state = ee.Image().byte().paint({
                featureCollection: shpEstados, color: 1,  width: 1.5});

var outline_Mun = ee.Image().byte().paint({
                    featureCollection: shpMun, color: 1,  width: 1.5});

Map.addLayer(basemapPlanet, vis.planet, 'planet geral', false);
Map.addLayer(polygonFotov, vis.poligonosFV, 'polygons FotoVolt', false);
Map.addLayer(fotovol_pred, vis.clusters, 'fotoVolt pred');
Map.addLayer(regionsFotoV, vis.regiones, 'region FotoVolt', false);
Map.centerObject(ee.Feature(regSelect.get(numbPol)), 16);
Map.setOptions("SATELLITE");
Map.addLayer(outline_state, {palette: 'FF0000'}, 'Estados');
Map.addLayer(outline_Mun, {palette: '00FF00'}, 'Municipios', false);



