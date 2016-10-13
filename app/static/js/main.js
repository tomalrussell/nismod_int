var APP = {
    layers: {}
}

var map_locations = {
    gaza: {
        lon: 34.4,
        lat: 31.4,
        zoom: 11
    }
}

var map = L.map('main-map').setView(map_locations.gaza, map_locations.gaza.zoom);

var basemap_url = "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"

L.tileLayer(basemap_url, {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>'
}).addTo(map);

APP.layers.base_lines = L.layerGroup().addTo(map);

var node_icon_html_by_type = {
    "bank": '<i class="fa fa-money" aria-hidden="true"></i>',
    "electricity_source": '<i class="fa fa-bolt" aria-hidden="true"></i>',
    "electricity_sink": '<i class="fa fa-bolt" aria-hidden="true"></i>',
    "fuel": '<i class="fa fa-car" aria-hidden="true"></i>',
    "hospital": '<i class="fa fa-hospital-o" aria-hidden="true"></i>',
    "school": '<i class="fa fa-graduation-cap" aria-hidden="true"></i>',
    "waste_water_treatment": '<i class="fa fa-tint" aria-hidden="true"></i>',
    "water_treatment": '<i class="fa fa-tint" aria-hidden="true"></i>',
    "unknown": '<i class="fa fa-question" aria-hidden="true"></i>'
}

function setup(data){
    var features_by_type = _.groupBy(data.features, function(feature){
        return feature.properties.type;
    });
    _.map(features_by_type, function(features, type){
        APP.layers[type] = addLayer(features);
    });
}

function addLayer(features){
    return L.geoJSON(features, {
        pointToLayer: function (feature, latlng) {
            var html = node_icon_html_by_type[feature.properties.type];
            if (html === undefined){
                html = node_icon_html_by_type["unknown"];
            }
            var marker = L.marker(latlng, {
                icon: L.divIcon({
                    html: html,
                    iconSize: [18, 18]
                })
            });

            marker._leaflet_id = feature.properties.id;

            marker.on("click", function(e){
                if(this._icon.classList.contains("icon-focus")){
                    this._icon.classList.remove("icon-focus");
                    closeDetails(this.feature);
                } else {
                    this._icon.classList.add("icon-focus");
                    showDetails(this.feature);
                }
            });
            return marker;
        },

    }).addTo(map);
}

function showDetails(feature){
    var mountNode = document.querySelector(".main-controls");
    console.log(feature.properties);
    var details_el = createDetailsEl(feature.properties);
    mountNode.innerHTML = "";
    mountNode.appendChild(details_el);

    // get geojson of all electricity_source_features and find the nearest
    var electricity_source_features = APP.layers.electricity_source.toGeoJSON();
    var nearest_electricity_source = turf.nearest(feature, electricity_source_features);

    // add class to highlight nearest_electricity_source
    var layer = APP.layers.electricity_source.getLayer(nearest_electricity_source.properties.id);
    layer._icon.classList.add("icon-dependent");

    // draw line from this feature to nearest_electricity_source
    var line = L.geoJSON(turf.lineString([feature.geometry.coordinates,nearest_electricity_source.geometry.coordinates]), {color: "#3399ff"});
    APP.layers.base_lines.addLayer(line);
}

function closeDetails(feature){
    var mountNode = document.querySelector(".main-controls");
    mountNode.innerHTML = "";

    APP.layers.base_lines.clearLayers();
}

function createDetailsEl(props){
    var wrap = document.createElement("div");
    var name_key = document.createElement("h3");
    var name_value = document.createElement("p");
    var type_key = document.createElement("h3");
    var type_value = document.createElement("p");
    var type_icon = document.createElement("span");
    var type_value_text = document.createElement("span");


    name_key.className = "details-key";
    name_key.textContent = "Name";
    wrap.appendChild(name_key);

    name_value.className = "details-value";
    name_value.textContent = props.name;
    wrap.appendChild(name_value);

    type_key.className = "details-key";
    type_key.textContent = "Type";
    wrap.appendChild(type_key);

    type_value.className = "details-value";

    type_icon.innerHTML = node_icon_html_by_type[props.type]
    type_value.appendChild(type_icon);

    type_value_text.textContent = props.type.replace("_"," ");
    type_value.appendChild(type_value_text);

    wrap.appendChild(type_value);

    return wrap;
}


// assume localStorage available
// run localStorage.clear() from console to flush
var cached = localStorage.getItem('gaza_infrastructure.json')
if(cached !== null){
    var data = JSON.parse(cached);
    console.log(data);
    setup(data, map);
} else {
    fetch('/data/gaza_infrastructure.json')
    .then(function(response){
        return response.json().then(function(json){
            localStorage.setItem('gaza_infrastructure.json', JSON.stringify(json));
            setup(json, map);
        });
    });
}

