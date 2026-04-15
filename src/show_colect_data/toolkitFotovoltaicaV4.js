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
var toolkitStyle = {
    tilePanel: {
        stretch: 'horizontal',
        textAlign: 'center',
        fontWeight: 'bold',
        fontSize: '24px'
    }, 
    painelcontrol: {
        width: '240px'
    }
}
// === scripts com poligonos feitos 
// https://code.earthengine.google.com/5f243cd97de0ac2aadff70e4b8ff2997
var param = {
    'asset_fotovol_predv4' : 'projects/geo-data-s/assets/fotovoltaica/version_4',    
    'asset_fotovol_predVC' : 'projects/geo-data-s/assets/fotovoltaica/version_2_clean',
    'assetNICFI': 'projects/planet-nicfi/assets/basemaps/americas',
    "asset_biomas_raster" : 'projects/mapbiomas-workspace/AUXILIAR/biomas-raster-41',
    "regions_on_paneis_foto": "projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons/buffer_5km_fotovolt_final_id",
    'asset_output_Polygons': 'projects/mapbiomas-workspace/AMOSTRAS/col9/CAATINGA/Energias/polygons',
    'lstYear': [2015,2016,2017,2018,2019,2020,2021,2022,2023,2024, 2025]    
}
var mapasRegGrid = null;


// This collection is not publicly accessible. To sign up for access,
// please see https://developers.planet.com/docs/integrations/gee/nicfi
var nicfi = ee.ImageCollection(param.assetNICFI);
print('imagens nicfi', nicfi)
var regionsFotoV = ee.FeatureCollection(param.regions_on_paneis_foto);
print(" regionms rectagular fotovoltaicas ", regionsFotoV.size());
print("show metadata of regions ", regionsFotoV);

var fotovol_predV4 = ee.ImageCollection(param.asset_fotovol_predv4);
print("show metadata de fotovoltaica ", fotovol_predV4);
fotovol_predV4 = fotovol_predV4.map(
                        function(img){
                            // reg_00000000000000000000_2015_10_pred
                            var sysId = img.id();
                            var partes = ee.List(ee.String(sysId).split("_"));
                            return img.set('idCod', partes.get(1));
                        });
print("show metadata de fotovoltaica modified ", fotovol_predV4);
var lstRegions = regionsFotoV.reduceColumns(ee.Reducer.toList(), ['idCod']).get('list');//.getInfo();
lstRegions = ee.List(lstRegions).distinct();

var keyListReg = lstRegions.map(
                    function(codigo){
                        var iCod = ee.String(codigo);
                        iCod = iCod.slice(ee.Number(iCod.length().subtract(5)), iCod.length());
                        return iCod;
                    });

var dictRegFV = ee.Dictionary.fromLists(keyListReg, ee.List(lstRegions));
print("dictionary of regions builded", dictRegFV);
lstRegions = lstRegions.getInfo();
var idRegactivo = lstRegions[13];
print('idRegactivo => ' + idRegactivo);

function ShowLayerFotovoltaicaActiva(idRegAct){

    var regionActiva = regionsFotoV.filter(ee.Filter.eq('system:index', idRegAct)).first().geometry();
    print('regionActiva' , regionActiva);

    // create a map for each band combo
    var imgYY = null;
    var maps = [];
    param.lstYear.forEach(function(nyear) {
        var map = ui.Map();
        map.add(ui.Label(nyear));
        var date_inic = ee.Date.fromYMD(nyear, 11, 1);
        var date_end = date_inic.advance(1, 'month');
        if (nyear == 2025){
            date_inic = ee.Date.fromYMD(nyear, 2, 1);
            date_end = date_inic.advance(1, 'month');
        }else{
            if (nyear < 2020){
                date_inic = ee.Date.fromYMD(nyear, 6, 1);
                date_end = date_inic.advance(7, 'month');
            }
        }
        imgYY = nicfi.filterDate(date_inic, date_end).first(); //.clip(regionActiva)
        var fotoPredYY = fotovol_predV4
                            .filter(ee.Filter.eq('idCod', idRegAct))
                            .filter(ee.Filter.eq('year', nyear));

        // fotoPredYY = fotoPredYY.clip(regionActiva)
        print(" in idCod " + fotoPredYY + " and year " + nyear + "we have ", fotoPredYY);
        
        fotoPredYY = fotoPredYY.max()
        map.addLayer(imgYY, vis.planet, "mos_" + nyear);
        map.addLayer(fotoPredYY.selfMask(), vis.clustersV1, 'fotoVol'); //.eq(1), 
        map.centerObject(regionActiva, 14);
        // map.setControlVisibility(false);
        maps.push(map);
    });
    var map = ui.Map();
    map.add(ui.Label('2024'));
    map.addLayer(imgYY, vis.planet, "mos_2024");
    map.setControlVisibility(false);
    
    maps.push(map);
    map = ui.Map();
    map.add(ui.Label('2024'));
    map.addLayer(ee.Image.constant(1), {min:0, max: 1}, "branco");
    // var fotoPredYY = fotovol_predV4.filter(ee.Filter.eq('year', 2024)).first();
    // map.addLayer(fotoPredYY, {min:0, max: 1}, "branco");
    map.setControlVisibility(false);
    // map.centerObject(imgYY.geometry(), 14);
    maps.push(map);
    // center the maps near Santa Cruz
    ui.Map.Linker(maps, 'change-bounds');
    // create a grid of maps.
    var mapGrid = ui.Panel([
            ui.Panel([maps[0], maps[1], maps[2], maps[3]],   null, {stretch: 'both'}),
            ui.Panel([maps[4], maps[5], maps[6], maps[7]],   null, {stretch: 'both'}),
            ui.Panel([maps[8], maps[9], maps[10], maps[11]], null, {stretch: 'both'}),
        ],
        ui.Panel.Layout.Flow('horizontal'), {stretch: 'both'}
    );
    return mapGrid;
}


mapasRegGrid = ShowLayerFotovoltaicaActiva(idRegactivo);

// create a title.
var title = ui.Label('Panel de paneis FotoVoltaicos /n ', toolkitStyle.tilePanel);
var select = ui.Select({
    items: lstRegions,
    placeholder: 'Choose a Fotovoltaica Id',
    value: idRegactivo,
    onChange: function(key) {
        print("IdCod selecionado ", key); 
        mapasRegGrid = ShowLayerFotovoltaicaActiva(key);     
        ui.root.widgets().reset([mapasRegGrid, controlPanel]);
        var Centor = regionsFotoV.filter(ee.Filter.eq('idCod', key));

    }
});

// control panel
var controlPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: toolkitStyle.painelcontrol
});

controlPanel.add(title);
controlPanel.add(select)

// add the maps and title to the ui.root
ui.root.widgets().reset([mapasRegGrid, controlPanel]);
ui.root.setLayout(ui.Panel.Layout.Flow('horizontal'));

