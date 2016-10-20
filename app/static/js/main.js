(function(window, document, undefined){

// APP global to hold application state for direct reference
var APP = window.APP = {
    layers: {}
}

// possible locations for map view
// - could load from database areas table?
APP.map_locations = {
    gaza: {
        lon: 34.4,
        lat: 31.4,
        zoom: 11
    }
}

// set up leaflet map with plain geographical base layer
var map = L.map('main-map').setView(APP.map_locations.gaza, APP.map_locations.gaza.zoom);
var basemap_url = "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
L.tileLayer(basemap_url, {
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>'
}).addTo(map);

// layer to hold lines (added first to draw under subsequent point layers)
APP.layers.base_lines = L.layerGroup().addTo(map);


function get_icon_html(type){
    // map from feature type to fontawesome icon
    var node_icon_class_by_type = {
        "bank": 'money',
        "electricity_source": 'bolt',
        "electricity_sink": 'bolt',
        "fuel": 'car',
        "hospital": 'hospital-o',
        "school": 'graduation-cap',
        "waste_water_treatment": 'tint',
        "water_treatment": 'tint',
        "unknown": 'question'
    }
    var icon_class = node_icon_class_by_type[type];
    if(icon_class === undefined){
         icon_class = node_icon_class_by_type["unknown"];
    }
    return '<i class="fa fa-'+icon_class+'" aria-hidden="true"></i>';
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
            // create marker for this feature with an icon
            var html = get_icon_html(feature.properties.type);
            var marker = L.marker(latlng, {
                icon: L.divIcon({
                    html: html,
                    iconSize: [18, 18]
                })
            });

            // set up id for ease of reference later
            marker._leaflet_id = feature.properties.id;

            // define click interaction, to show details on focus
            marker.on("click", function(e){
                if(this._icon.classList.contains("icon-focus")){
                    // remove focus from this feature
                    this._icon.classList.remove("icon-focus");
                    closeDetails(this.feature);
                } else {
                    // remove focus from any other features
                    _.each(document.querySelectorAll(".icon-focus"), function(el){
                        el.classList.remove("icon-focus");
                    });
                    // focus on this feature
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
    // clear/close details sidebar
    var mountNode = document.querySelector(".main-controls");
    mountNode.innerHTML = "";

    APP.layers.base_lines.clearLayers();
}

function createDetailsEl(props){
    // template for details sidebar
    // - could use template library (react/mustache?) if there's a need for
    //   more complex templating and data updates
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

    type_icon.innerHTML = get_icon_html(props.type);
    type_value.appendChild(type_icon);

    type_value_text.textContent = props.type.replace("_"," ");
    type_value.appendChild(type_value_text);

    wrap.appendChild(type_value);

    return wrap;
}

function clear_cache(){
    localStorage.clear();
}

function clear_cache_and_reload(){
    clear_cache();
    window.location.reload(false);
}

var reload_button = document.querySelector(".clear-cache-reload");
if (reload_button){
    reload_button.addEventListener("click", function(e){
        e.preventDefault();
        clear_cache_and_reload();
    });
}

// assume localStorage available
// - could 'cut the mustard' and fall back to no js for older browsers
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

})(window, document);