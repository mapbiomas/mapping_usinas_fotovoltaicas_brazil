var vis = {
    planet: {
        'min':14,
        'max':3454,
        'bands': ['R','G','B']
    },
    indexIIA :{
        min: 0, max:1, 
        palette: ["#6a8d73","#f4fdd9","#e4ffe1","#ffe8c2","#f0a868"]
    },
    indexGLI: {
        min: 0, max:1, 
        palette: ["#fae3e3","#f7d4bc","#cfa5b4","#c98bb9","#846b8a"]
    }, 
    clusters: {
        min: 0, max: 2,
        palette: ["#600504","#6b0504","#d5e68d"]
    },
    clusterMask: {
        min: 0, max: 1,
        palette: ["#6b0504"]
    }
};

var param = {
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    'asset_regions_FV': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_19_11',
    'asset_regions_FVcorr': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/regions_on_paneis_fotovoltaicos_26_11_corr',
    "asset_bioma_shp": 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil'
}


var biomashp = ee.FeatureCollection(param.asset_bioma_shp).geometry().dissolve();
var bioCaat = ee.Image(param.asset_biomas_raster).gt(0)

// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
// Filter basemaps by date and get the first image from filtered results
var basemapPlanet = nicfi.filter(ee.Filter.date('2024-10-01','2024-11-20')).first();
basemapPlanet = basemapPlanet.updateMask(bioCaat);     


var region_toPred = ee.FeatureCollection(param.asset_regions_FV);
print('show metadata Fotovoltaica ', region_toPred);

var region_toPredcor = ee.FeatureCollection(param.asset_regions_FVcorr);
print('show metadata Fotovoltaica Corregido ', region_toPredcor);

var oneFeat = region_toPredcor.filter(ee.Filter.eq('idCod', '00000000000000000080')).geometry();

Map.addLayer(basemapPlanet, vis.planet, 'planet geral');
Map.addLayer(region_toPred, {color: 'red'}, 'regions predict');
Map.addLayer(region_toPredcor, {color: 'blue'}, 'regions predict Corr');
Map.addLayer(oneFeat, {color:'yellow'}, 'one')
Map.centerObject(oneFeat, 12)