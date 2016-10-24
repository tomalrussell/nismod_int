(function(window, document, undefined){

// APP global to hold application state for direct reference
var APP = window.APP = {
    // layers is a collection of leaflet map layers
    // each layer contains related features (typically grouped by type)
    layers: {},

    // layer_key => boolean, indicating whether is layer is active or not
    activeLayers: {},
    utilLayerKeys: [],

    // possible locations for map view
    // - could load from database areas table?
    map_locations: {
        gaza: {
            lon: 34.4,
            lat: 31.4,
            zoom: 11
        }
    },

    // leaflet map
    map: undefined
}

function setupMap(){
    // set up leaflet map with plain geographical base layer
    var map = APP.map = L.map('main-map').setView(APP.map_locations.gaza, APP.map_locations.gaza.zoom);
    var basemap_url = "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
    L.tileLayer(basemap_url, {
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>'
    }).addTo(map);

    // layer to hold lines (added first to draw under subsequent point layers)
    APP.layers.base_lines = L.layerGroup().addTo(map);
    // save to list of util layers, e.g not to show in nav
    APP.utilLayerKeys.push("base_lines");
}

function setupMapData(data){
    var features_by_type = _.groupBy(data.features, function(feature){
        return feature.properties.type;
    });
    _.map(features_by_type, function(features, type){
        APP.layers[type] = addLayer(features);
        APP.activeLayers[type] = true;
    });

    updateTypeNav();

    var controls_form = document.querySelector(".main-controls");
    controls_form.addEventListener("change", updateActiveLayers);
}

function getIconHtml(type){
    // map from feature type to fontawesome icon
    var node_icon_class_by_type = {
        "bank": 'money',
        "electricity_source": 'bolt',
        "electricity_sink": 'bolt',
        "fuel": 'car',
        "hospital": 'hospital-o',
        "school": 'graduation-cap',
        "tower": 'wifi',
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

function addLayer(features){
    return L.geoJSON(features, {
        pointToLayer: function (feature, latlng) {
            // create marker for this feature with an icon
            var html = getIconHtml(feature.properties.type);
            var marker = L.marker(latlng, {
                icon: L.divIcon({
                    html: html,
                    iconSize: [18, 18]
                })
            });

            // set up id for ease of reference later
            marker._leaflet_id = feature.properties.type + feature.properties.id;

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
        }
    }).addTo(APP.map);
}

function showDetails(feature){
    var mountNode = document.querySelector(".main-controls .node-details");
    var details_el = createDetailsEl(feature.properties);
    mountNode.innerHTML = "";
    mountNode.appendChild(details_el);
}

function highlightDependency(feature, dependency){
    // add class to highlight dependency
    var marker = APP.layers[dependency.properties.type].getLayer(dependency.properties.type + dependency.properties.id);
    marker._icon.classList.add("icon-dependent");

    // draw line from this feature to dependency
    var line = L.geoJSON(turf.lineString([feature.geometry.coordinates,dependency.geometry.coordinates]), {color: "#3399ff"});
    APP.layers.base_lines.addLayer(line);
}

function closeDetails(feature){
    // clear/close details sidebar
    var mountNode = document.querySelector(".main-controls .node-details");
    mountNode.innerHTML = "";

    // clear all dependency lines
    APP.layers.base_lines.clearLayers();
}

function updateTypeNav(){
    var nav_el = document.querySelector(".main-controls .node-types-nav");
    nav_el.innerHTML = "";
    var sorted_keys = _.keys(APP.activeLayers).sort()

    _.each(sorted_keys, function(key){
        var link_el
        if ( !_.contains(APP.utilLayerKeys, key) ){
            link_el = createTypeNavEl({"type": key, "active": APP.activeLayers[key]});
            nav_el.appendChild(link_el);
        }
    });
}

function updateActiveLayers(){
    _.each(APP.activeLayers, function(was_active, key){
        var checkbox = document.querySelector("#node_type_"+key);
        var layer = APP.layers[key];

        if (checkbox){
            if(checkbox.checked){
                if(!was_active){
                    APP.map.addLayer(layer);
                }
            } else {
                if(was_active){
                    APP.map.removeLayer(layer);
                }
            }

            APP.activeLayers[key] = checkbox.checked;
        }
    });
}

function createTypeNavEl(props){
    var wrap = document.createElement("div");
    var input = document.createElement("input")
    var label = document.createElement("label");
    var type_icon = document.createElement("span");
    var type_value_text = document.createElement("span");

    input.setAttribute("value", props.type);
    input.setAttribute("id", "node_type_"+props.type);
    input.setAttribute("name", "node_types[]")
    input.setAttribute("type", "checkbox")
    if(props.active){
        input.setAttribute("checked", "checked");
    }

    label.classList.add("button-link");
    label.setAttribute("for", "node_type_"+props.type);


    type_icon.innerHTML = getIconHtml(props.type);
    label.appendChild(type_icon);

    type_value_text.textContent = props.type.replace(/_/g," ");
    label.appendChild(type_value_text);

    wrap.appendChild(input);
    wrap.appendChild(label);

    return wrap;
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

    type_icon.innerHTML = getIconHtml(props.type);
    type_value.appendChild(type_icon);

    type_value_text.textContent = props.type.replace(/_/g," ");
    type_value.appendChild(type_value_text);

    wrap.appendChild(type_value);

    return wrap;
}

function clear_cache(){
    localStorage.clear();
}

function clear_cache_and_reload(){
    clear_cache();
    window.location.reload(true);
}

function init(){
    setupMap();

    var reload_button = document.querySelector(".clear-cache-reload");
    if (reload_button){
        reload_button.addEventListener("click", function(e){
            e.preventDefault();
            clear_cache_and_reload();
        });
    }

    // assume localStorage available
    // - could 'cut the mustard' and fall back to no js for older browsers
    var cached = localStorage.getItem('gaza')
    if(cached !== null){
        var data = JSON.parse(cached);
        setupMapData(data, APP.map);
    } else {
        fetch('/data/gaza')
        .then(function(response){
            return response.json().then(function(json){
                localStorage.setItem('gaza', JSON.stringify(json));
                setupMapData(json, APP.map);
            });
        });
    }
}

init();

})(window, document);
