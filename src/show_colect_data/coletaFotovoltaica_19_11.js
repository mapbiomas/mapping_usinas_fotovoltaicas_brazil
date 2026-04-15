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
// === scripts com poligonos feitos 
// https://code.earthengine.google.com/d664a562fb29a09c8d465be23740e5e7
var param = {
    'asset_eolica' : 'projects/mapbiomas-arida/eol_existente',
    'aaset_fotovol': 'projects/mapbiomas-arida/ufv_existente',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    "asset_output_raster": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/rotulos',
    "asset_output_shp": 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',
    "asset_bioma_shp": 'projects/mapbiomas-workspace/AUXILIAR/biomas_IBGE_250mil'
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
var ExportarMapsLabelAsset = function(image_map, name_img, regiao){
  
    var assetIdss = 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/';
    var paramExpA = {
        image: image_map.selfMask(), 
        description: name_img , 
        assetId: assetIdss + name_img, 
        pyramidingPolicy: {".default": "mode"},
        scale: 3, 
        maxPixels: 1e14, 
        region: regiao
    };
    Export.image.toAsset(paramExpA);     
    print("Export map label to Asset" + name_img + " ....");

}

var numbPol = '_22'
var biomashp = ee.FeatureCollection(param.asset_bioma_shp).geometry().dissolve();
var bioCaat = ee.Image(param.asset_biomas_raster).gt(0)//.eq(5)
                    // .add( ee.Image(param.asset_biomas_raster).eq(4))
                        // .add(ee.Image(param.asset_biomas_raster).eq(2))
                  
// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
// Filter basemaps by date and get the first image from filtered results
var basemapPlanet = nicfi.filter(ee.Filter.date('2024-10-01','2024-11-20')).first();
basemapPlanet = basemapPlanet.updateMask(bioCaat);             

var layerFotov = ee.FeatureCollection(param.aaset_fotovol);
print(" we have loaded fotovolt layer with ", layerFotov.size());
print(layerFotov.first())
var fotoList = layerFotov.toList(239);
var posIndex = 1;
var setPosFoto = ee.Feature(ee.List(fotoList).get(posIndex)); //mudar aqui
// Map.centerObject(setPosFoto.geometry(), 16);
var fotovolSelect = layerFotov.filterBounds(polygon_fotov.geometry()).first()
print("Ver metadatas ", fotovolSelect);
//var nomefoto = fotovolSelect.get('ceg').getInfo();
//print(nomefoto)
var nomefoto = "grupo_fotovoltaico";
// var specialChars = "!@#$^&%*()+=-[]\/{}|:<>?,.";
// nomefoto = ee.String(nomefoto).replace('/[.]',"_");
// print("ver o nome ", nomefoto);

// Processso de clusters Fotovoltaicas

print("show metadata polygon Fotovoltaica ", Fotov_limites);
// var featArea_eolica = ee.Feature(Region_fotov, {'class': 1});
// print("feat area ", featArea_eolica);
var maskArea_fotov = ee.FeatureCollection(Fotov_limites).reduceToImage({
                                    properties: ['class'], reducer: ee.Reducer.first()});


Map.addLayer(basemapPlanet, vis.planet, 'planet geral');
Map.addLayer(layerFotov, {color: '#660e60'}, 'fotov');

var point_Exp = ee.FeatureCollection(feito_ponto).merge(ee.FeatureCollection(coletar));
print("Total de points coletados ", point_Exp.size())
var name_export_shp = 'pontos_NearorIn_paneis_fotovoltaicos_19_11';
processoExportar(point_Exp, name_export_shp);

name_export_shp = 'regions_on_paneis_fotovoltaicos_19_11';
processoExportar(ee.FeatureCollection(revisado), name_export_shp);
Map.setOptions("SATELLITE");

// Map.centerObject(polygon_fotov,12)

name_export_shp = 'polygons_base_paneis_fotovoltaicos_19_11';
processoExportar(ee.FeatureCollection(Fotov_limites), name_export_shp);

var name_export_raster = 'label_base_paneis_fotovoltaicos_19_11';
ExportarMapsLabelAsset(maskArea_fotov.selfMask().toByte(), name_export_raster, biomashp)

