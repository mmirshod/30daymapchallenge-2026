var wms_layers = [];

var format_water_bodies_tashkentnatural_water_0 = new ol.format.GeoJSON();
var features_water_bodies_tashkentnatural_water_0 = format_water_bodies_tashkentnatural_water_0.readFeatures(json_water_bodies_tashkentnatural_water_0, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_water_bodies_tashkentnatural_water_0 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_water_bodies_tashkentnatural_water_0.addFeatures(features_water_bodies_tashkentnatural_water_0);
var lyr_water_bodies_tashkentnatural_water_0 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_water_bodies_tashkentnatural_water_0, 
                style: style_water_bodies_tashkentnatural_water_0,
                popuplayertitle: 'water_bodies_tashkent — natural_water',
                interactive: false,
                title: '<img src="styles/legend/water_bodies_tashkentnatural_water_0.png" /> water_bodies_tashkent — natural_water'
            });
var format_tashkent_districtsadm_districts_1 = new ol.format.GeoJSON();
var features_tashkent_districtsadm_districts_1 = format_tashkent_districtsadm_districts_1.readFeatures(json_tashkent_districtsadm_districts_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_tashkent_districtsadm_districts_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_tashkent_districtsadm_districts_1.addFeatures(features_tashkent_districtsadm_districts_1);
var lyr_tashkent_districtsadm_districts_1 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_tashkent_districtsadm_districts_1, 
                style: style_tashkent_districtsadm_districts_1,
                popuplayertitle: 'tashkent_districts — adm_districts',
                interactive: true,
                title: '<img src="styles/legend/tashkent_districtsadm_districts_1.png" /> tashkent_districts — adm_districts'
            });
var format_gorets_points_2 = new ol.format.GeoJSON();
var features_gorets_points_2 = format_gorets_points_2.readFeatures(json_gorets_points_2, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_gorets_points_2 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_gorets_points_2.addFeatures(features_gorets_points_2);
var lyr_gorets_points_2 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_gorets_points_2, 
                style: style_gorets_points_2,
                popuplayertitle: 'gorets_points копия',
                interactive: true,
    title: 'gorets_points копия<br />\
    <img src="styles/legend/gorets_points_2_0.png" /> 21 Мираж<br />\
    <img src="styles/legend/gorets_points_2_1.png" /> 21 Горизонт<br />' });

lyr_water_bodies_tashkentnatural_water_0.setVisible(true);lyr_tashkent_districtsadm_districts_1.setVisible(true);lyr_gorets_points_2.setVisible(true);
// var layersList = [lyr_water_bodies_tashkentnatural_water_0,lyr_tashkent_districtsadm_districts_1,lyr_gorets_points_2];
var layersList = [
    lyr_gorets_points_2
];

var lyr_TerrainTiles = new ol.layer.Tile({
    title: "Топографический рельеф",
    // type: "base",
    visible: true,
    source: new ol.source.XYZ({
        url: "./terrain_tiles/{z}/{x}/{y}.png",
        projection: "EPSG:3857",
        maxZoom: 13,
        wrapX: false,
        attributions: [
            "Copernicus DEM GLO-30",
            "© OpenStreetMap contributors"
        ]
    })
});


lyr_water_bodies_tashkentnatural_water_0.set('fieldAliases', {'fid': 'fid', 'full_id': 'full_id', 'osm_id': 'osm_id', 'osm_type': 'osm_type', 'natural': 'natural', 'basin': 'basin', 'access': 'access', 'golf': 'golf', 'building:levels': 'building:levels', 'building': 'building', 'noname': 'noname', 'fee': 'fee', 'sport': 'sport', 'alt_name:ru': 'alt_name:ru', 'waterway': 'waterway', 'name:uz-Cyrl': 'name:uz-Cyrl', 'addr:country': 'addr:country', 'name:ja': 'name:ja', 'architect:wikipedia': 'architect:wikipedia', 'alt_name:en': 'alt_name:en', 'ele': 'ele', 'landuse': 'landuse', 'tourism': 'tourism', 'man_made': 'man_made', 'layer': 'layer', 'height': 'height', 'place': 'place', 'leisure': 'leisure', 'wikimedia_commons': 'wikimedia_commons', 'lit': 'lit', 'drinking_water': 'drinking_water', 'amenity': 'amenity', 'name:ky': 'name:ky', 'ref': 'ref', 'alt_name:uz': 'alt_name:uz', 'water_supply': 'water_supply', 'water_source': 'water_source', 'old_name': 'old_name', 'boat': 'boat', 'alt_name': 'alt_name', 'wikipedia:ru': 'wikipedia:ru', 'name:fa': 'name:fa', 'name:eo': 'name:eo', 'name:de': 'name:de', 'int_name': 'int_name', 'gns:ufi': 'gns:ufi', 'gns:dsg': 'gns:dsg', 'tidal': 'tidal', 'salt': 'salt', 'intermittent': 'intermittent', 'fishing': 'fishing', 'name:uz': 'name:uz', 'name:kk': 'name:kk', 'wikipedia': 'wikipedia', 'wikidata': 'wikidata', 'name:ru': 'name:ru', 'name:en': 'name:en', 'name': 'name', 'water': 'water', 'type': 'type', });
lyr_tashkent_districtsadm_districts_1.set('fieldAliases', {'fid': 'fid', 'shapeName': 'shapeName', 'shapeISO': 'shapeISO', 'shapeID': 'shapeID', 'shapeGroup': 'shapeGroup', 'shapeType': 'shapeType', });
lyr_gorets_points_2.set('fieldAliases', {'fid': 'fid', 'ele': 'ele', 'time': 'time', 'magvar': 'magvar', 'geoidheight': 'geoidheight', 'name': 'Название', 'cmt': 'cmt', 'desc': 'desc', 'src': 'src', 'link1_href': 'link1_href', 'link1_text': 'link1_text', 'link1_type': 'link1_type', 'link2_href': 'link2_href', 'link2_text': 'link2_text', 'link2_type': 'link2_type', 'sym': 'sym', 'type': 'type', 'fix': 'fix', 'sat': 'sat', 'hdop': 'hdop', 'vdop': 'vdop', 'pdop': 'pdop', 'ageofdgpsdata': 'ageofdgpsdata', 'dgpsid': 'dgpsid', 'osmand_address': 'osmand_address', 'osmand_osm_tag_wikimedia_commons': 'osmand_osm_tag_wikimedia_commons', 'osmand_icon': 'osmand_icon', 'osmand_osm_tag_ele': 'Высота (м)', 'osmand_osm_tag_wikidata': 'osmand_osm_tag_wikidata', 'osmand_osm_tag_wikipedia_-_ru': 'osmand_osm_tag_wikipedia_-_ru', 'osmand_amenity_type': 'osmand_amenity_type', 'osmand_osm_tag_summit_cross': 'osmand_osm_tag_summit_cross', 'osmand_osm_tag_wikipedia_-_en': 'osmand_osm_tag_wikipedia_-_en', 'osmand_amenity_subtype': 'osmand_amenity_subtype', 'osmand_amenity_name': 'osmand_amenity_name', 'osmand_osm_tag_viewpoint': 'osmand_osm_tag_viewpoint', 'osmand_osm_tag_wikipedia': 'osmand_osm_tag_wikipedia', 'osmand_osm_tag_peak': 'osmand_osm_tag_peak', 'osmand_osm_tag_survey_point': 'osmand_osm_tag_survey_point', 'osmand_osm_tag_alt_name': 'osmand_osm_tag_alt_name', 'osmand_osm_tag_attraction': 'osmand_osm_tag_attraction', 'osmand_osm_tag_official_name': 'osmand_osm_tag_official_name', 'osmand_osm_tag_alt_name_-_ru': 'osmand_osm_tag_alt_name_-_ru', 'osmand_color': 'osmand_color', 'osmand_osm_tag_route_id': 'osmand_osm_tag_route_id', 'osmand_collapsable_water_type': 'osmand_collapsable_water_type', 'osmand_osm_tag_salt_no': 'osmand_osm_tag_salt_no', 'osmand_osm_tag_intermittent': 'osmand_osm_tag_intermittent', 'osmand_osm_tag_salt_yes': 'osmand_osm_tag_salt_yes', 'osmand_osm_tag_note': 'osmand_osm_tag_note', 'layer': 'layer', 'path': 'path', 'program': 'Программа', 'difficulty': 'difficulty', });
lyr_water_bodies_tashkentnatural_water_0.set('fieldImages', {'fid': '', 'full_id': '', 'osm_id': '', 'osm_type': '', 'natural': '', 'basin': '', 'access': '', 'golf': '', 'building:levels': '', 'building': '', 'noname': '', 'fee': '', 'sport': '', 'alt_name:ru': '', 'waterway': '', 'name:uz-Cyrl': '', 'addr:country': '', 'name:ja': '', 'architect:wikipedia': '', 'alt_name:en': '', 'ele': '', 'landuse': '', 'tourism': '', 'man_made': '', 'layer': '', 'height': '', 'place': '', 'leisure': '', 'wikimedia_commons': '', 'lit': '', 'drinking_water': '', 'amenity': '', 'name:ky': '', 'ref': '', 'alt_name:uz': '', 'water_supply': '', 'water_source': '', 'old_name': '', 'boat': '', 'alt_name': '', 'wikipedia:ru': '', 'name:fa': '', 'name:eo': '', 'name:de': '', 'int_name': '', 'gns:ufi': '', 'gns:dsg': '', 'tidal': '', 'salt': '', 'intermittent': '', 'fishing': '', 'name:uz': '', 'name:kk': '', 'wikipedia': '', 'wikidata': '', 'name:ru': '', 'name:en': '', 'name': '', 'water': '', 'type': '', });
lyr_tashkent_districtsadm_districts_1.set('fieldImages', {'fid': 'TextEdit', 'shapeName': 'TextEdit', 'shapeISO': 'TextEdit', 'shapeID': 'TextEdit', 'shapeGroup': 'TextEdit', 'shapeType': 'TextEdit', });
lyr_gorets_points_2.set('fieldImages', {'fid': 'TextEdit', 'ele': 'TextEdit', 'time': 'DateTime', 'magvar': 'TextEdit', 'geoidheight': 'TextEdit', 'name': 'TextEdit', 'cmt': 'TextEdit', 'desc': 'TextEdit', 'src': 'TextEdit', 'link1_href': 'TextEdit', 'link1_text': 'TextEdit', 'link1_type': 'TextEdit', 'link2_href': 'TextEdit', 'link2_text': 'TextEdit', 'link2_type': 'TextEdit', 'sym': 'TextEdit', 'type': 'TextEdit', 'fix': 'TextEdit', 'sat': 'Range', 'hdop': 'TextEdit', 'vdop': 'TextEdit', 'pdop': 'TextEdit', 'ageofdgpsdata': 'TextEdit', 'dgpsid': 'Range', 'osmand_address': 'TextEdit', 'osmand_osm_tag_wikimedia_commons': 'TextEdit', 'osmand_icon': 'TextEdit', 'osmand_osm_tag_ele': 'TextEdit', 'osmand_osm_tag_wikidata': 'TextEdit', 'osmand_osm_tag_wikipedia_-_ru': 'TextEdit', 'osmand_amenity_type': 'TextEdit', 'osmand_osm_tag_summit_cross': 'TextEdit', 'osmand_osm_tag_wikipedia_-_en': 'TextEdit', 'osmand_amenity_subtype': 'TextEdit', 'osmand_amenity_name': 'TextEdit', 'osmand_osm_tag_viewpoint': 'TextEdit', 'osmand_osm_tag_wikipedia': 'TextEdit', 'osmand_osm_tag_peak': 'TextEdit', 'osmand_osm_tag_survey_point': 'TextEdit', 'osmand_osm_tag_alt_name': 'TextEdit', 'osmand_osm_tag_attraction': 'TextEdit', 'osmand_osm_tag_official_name': 'TextEdit', 'osmand_osm_tag_alt_name_-_ru': 'TextEdit', 'osmand_color': 'TextEdit', 'osmand_osm_tag_route_id': 'TextEdit', 'osmand_collapsable_water_type': 'TextEdit', 'osmand_osm_tag_salt_no': 'TextEdit', 'osmand_osm_tag_intermittent': 'TextEdit', 'osmand_osm_tag_salt_yes': 'TextEdit', 'osmand_osm_tag_note': 'TextEdit', 'layer': 'TextEdit', 'path': 'TextEdit', 'program': 'TextEdit', 'difficulty': 'Range', });
lyr_water_bodies_tashkentnatural_water_0.set('fieldLabels', {'fid': 'hidden field', 'full_id': 'hidden field', 'osm_id': 'hidden field', 'osm_type': 'hidden field', 'natural': 'hidden field', 'basin': 'hidden field', 'access': 'hidden field', 'golf': 'hidden field', 'building:levels': 'hidden field', 'building': 'hidden field', 'noname': 'hidden field', 'fee': 'hidden field', 'sport': 'hidden field', 'alt_name:ru': 'hidden field', 'waterway': 'hidden field', 'name:uz-Cyrl': 'hidden field', 'addr:country': 'hidden field', 'name:ja': 'hidden field', 'architect:wikipedia': 'hidden field', 'alt_name:en': 'hidden field', 'ele': 'hidden field', 'landuse': 'hidden field', 'tourism': 'hidden field', 'man_made': 'hidden field', 'layer': 'hidden field', 'height': 'hidden field', 'place': 'hidden field', 'leisure': 'hidden field', 'wikimedia_commons': 'hidden field', 'lit': 'hidden field', 'drinking_water': 'hidden field', 'amenity': 'hidden field', 'name:ky': 'hidden field', 'ref': 'hidden field', 'alt_name:uz': 'hidden field', 'water_supply': 'hidden field', 'water_source': 'hidden field', 'old_name': 'hidden field', 'boat': 'hidden field', 'alt_name': 'hidden field', 'wikipedia:ru': 'hidden field', 'name:fa': 'hidden field', 'name:eo': 'hidden field', 'name:de': 'hidden field', 'int_name': 'hidden field', 'gns:ufi': 'hidden field', 'gns:dsg': 'hidden field', 'tidal': 'hidden field', 'salt': 'hidden field', 'intermittent': 'hidden field', 'fishing': 'hidden field', 'name:uz': 'hidden field', 'name:kk': 'hidden field', 'wikipedia': 'hidden field', 'wikidata': 'hidden field', 'name:ru': 'hidden field', 'name:en': 'hidden field', 'name': 'hidden field', 'water': 'hidden field', 'type': 'hidden field', });
lyr_tashkent_districtsadm_districts_1.set('fieldLabels', {'fid': 'hidden field', 'shapeName': 'hidden field', 'shapeISO': 'hidden field', 'shapeID': 'hidden field', 'shapeGroup': 'hidden field', 'shapeType': 'hidden field', });
lyr_gorets_points_2.set('fieldLabels', {'fid': 'hidden field', 'ele': 'hidden field', 'time': 'hidden field', 'magvar': 'hidden field', 'geoidheight': 'hidden field', 'name': 'header label - visible with data', 'cmt': 'hidden field', 'desc': 'hidden field', 'src': 'hidden field', 'link1_href': 'hidden field', 'link1_text': 'hidden field', 'link1_type': 'hidden field', 'link2_href': 'hidden field', 'link2_text': 'hidden field', 'link2_type': 'hidden field', 'sym': 'hidden field', 'type': 'hidden field', 'fix': 'hidden field', 'sat': 'hidden field', 'hdop': 'hidden field', 'vdop': 'hidden field', 'pdop': 'hidden field', 'ageofdgpsdata': 'hidden field', 'dgpsid': 'hidden field', 'osmand_address': 'hidden field', 'osmand_osm_tag_wikimedia_commons': 'hidden field', 'osmand_icon': 'hidden field', 'osmand_osm_tag_ele': 'inline label - visible with data', 'osmand_osm_tag_wikidata': 'hidden field', 'osmand_osm_tag_wikipedia_-_ru': 'hidden field', 'osmand_amenity_type': 'hidden field', 'osmand_osm_tag_summit_cross': 'hidden field', 'osmand_osm_tag_wikipedia_-_en': 'hidden field', 'osmand_amenity_subtype': 'hidden field', 'osmand_amenity_name': 'hidden field', 'osmand_osm_tag_viewpoint': 'hidden field', 'osmand_osm_tag_wikipedia': 'hidden field', 'osmand_osm_tag_peak': 'hidden field', 'osmand_osm_tag_survey_point': 'hidden field', 'osmand_osm_tag_alt_name': 'hidden field', 'osmand_osm_tag_attraction': 'hidden field', 'osmand_osm_tag_official_name': 'hidden field', 'osmand_osm_tag_alt_name_-_ru': 'hidden field', 'osmand_color': 'hidden field', 'osmand_osm_tag_route_id': 'hidden field', 'osmand_collapsable_water_type': 'hidden field', 'osmand_osm_tag_salt_no': 'hidden field', 'osmand_osm_tag_intermittent': 'hidden field', 'osmand_osm_tag_salt_yes': 'hidden field', 'osmand_osm_tag_note': 'hidden field', 'layer': 'hidden field', 'path': 'hidden field', 'program': 'inline label - visible with data', 'difficulty': 'hidden field', });
lyr_gorets_points_2.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});

// Добавить подложку ниже всех интерактивных слоёв
layersList.unshift(lyr_TerrainTiles);
