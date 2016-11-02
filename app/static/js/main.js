(function(window, document, undefined){

// APP global to hold application state for direct reference
var APP = window.APP = {
    // layers is a collection of leaflet map layers
    // each layer contains related features (typically grouped by type)
    layers: {},

    // hold another reference to nodes
    // node_id => leaflet marker
    nodes: {},

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

function setupMapNodes(data){
    // group nodes by type and add to map layers
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

function setupMapEdges(data){
    // build array of dependent/dependency ids on each node
    // - currently discarding other edge data
    _.each(data.features, function(feature){
        var from_node = APP.nodes[feature.properties.from_node_id]
        var to_node = APP.nodes[feature.properties.to_node_id]
        from_node.feature.properties.dependent_ids.push(feature.properties.to_node_id)
        to_node.feature.properties.dependency_ids.push(feature.properties.from_node_id)
    });
}

function getIconClass(type){
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
    return icon_class;
}

function getIconHtml(type){
    var icon_class = getIconClass(type);
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
            APP.nodes[feature.properties.id] = marker;

            // set up array of dependent_ids and dependency_ids
            // to be filled with data from edges
            // - could do this server side?
            // - each edge is currently just a straight-line dependency
            feature.properties.dependent_ids = []
            feature.properties.dependency_ids = []

            // define click interaction, to show details on focus
            marker.on("click", function(e){
                if(this._icon.classList.contains("icon-focus")){
                    // remove focus from this feature
                    this._icon.classList.remove("icon-focus");
                    closeDetails(this.feature);

                    // clear dependency lines
                    APP.layers.base_lines.clearLayers();

                    // remove focus from any dependent features
                    _.each(document.querySelectorAll(".icon-dependent"), function(el){
                        el.classList.remove("icon-dependent");
                    });

                } else {
                    // remove focus from any other features
                    _.each(document.querySelectorAll(".icon-focus, .icon-dependent"), function(el){
                        el.classList.remove("icon-focus", "icon-dependent");
                    });
                    // focus on this feature
                    this._icon.classList.add("icon-focus");
                    showDetails(this.feature);

                    // clear dependency lines
                    APP.layers.base_lines.clearLayers();

                    // highlight dependencies
                    _.each(this.feature.properties.dependent_ids, function(id){
                        var dependent_node = APP.nodes[id];
                        highlightDependency(this.feature, dependent_node.feature);
                    }, this);
                }
            });
            return marker;
        }
    }).addTo(APP.map);
}

function showDetails(feature){
    // populate node details element
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
    var line = L.geoJSON(turf.lineString([feature.geometry.coordinates, dependency.geometry.coordinates]), {color: "#3399ff"});
    APP.layers.base_lines.addLayer(line);
}

function closeDetails(feature){
    // clear/close details sidebar
    var mountNode = document.querySelector(".main-controls .node-details");
    mountNode.innerHTML = "";
}

function updateTypeNav(){
    // populate map layer checkbox list
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
    // read checkbox status to update map layers
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
    var template = `
    <input value="{{ type }}" id="node_type_{{ type }}" name="node_types[]" type="checkbox" {{#active}}checked="checked"{{/active}} >
    <label class="button-link" for="node_type_{{ type }}">
        <i class="fa fa-{{ icon_class }}" aria-hidden="true"></i>
        {{ type_text }}
    </label>
    `;
    Mustache.parse(template);

    props.icon_class = getIconClass(props.type);
    props.type_text = props.type.replace(/_/g," ");

    var rendered = Mustache.render(template, props);
    wrap.innerHTML = rendered;

    return wrap;
}

function createDetailsEl(props){
    // template for details sidebar
    // - using simple Mustache template - anything between {{ }} is replaced
    // - could use a more heavy-duty library (react?) if there's a need for
    //   more complex templating and data updates
    var wrap = document.createElement("div");
    var template = `
    <h4 class="details-key">Name</h4>
    <p class="details-value">{{ name }}</p>
    <h4 class="details-key">Type</h4>
    <p class="details-value">
        <i class="fa fa-{{ icon_class }}" aria-hidden="true"></i>
        {{ type_text }}
    </p>
    <a href="/nodes/{{ id }}.html" class="button-link">View</a>
    <a href="/nodes/{{ id }}.html?edit=true" class="button-link">Edit</a>`;
    Mustache.parse(template);

    props.icon_class = getIconClass(props.type);
    props.type_text = props.type.replace(/_/g," ");

    var rendered = Mustache.render(template, props);
    // mustache renders to a string, so set as innerHTML and return DOM node
    wrap.innerHTML = rendered;

    return wrap;
}

function clear_cache(){
    localStorage.clear();
}

function clear_cache_and_reload(){
    clear_cache();
    window.location.reload(true);
}


function cachingFetch(url, options) {
    // assume localStorage available
    // - could 'cut the mustard' and fall back to no js for older browsers
    let cached = localStorage.getItem(url)
    if (cached !== null) {
        return Promise.resolve(JSON.parse(cached));
    }
    return fetch(url, options).then(function(response){
        return response.json().then(function(json){
            localStorage.setItem(url, JSON.stringify(json));
            return json;
        });
    });
}

function init(){
    var mapEl = document.querySelector("#main-map");
    if(mapEl){
        setupMap();

        var reload_button = document.querySelector(".clear-cache-reload");
        if (reload_button){
            reload_button.addEventListener("click", function(e){
                e.preventDefault();
                clear_cache_and_reload();
            });
        }

        // TODO handle 404, timeout
        cachingFetch('/nodes.json?area=gaza')
        .then(function(json){
            setupMapNodes(json, APP.map);
        })
        .then(function(){
            cachingFetch('/edges.json')
            .then(function(json){
                setupMapEdges(json, APP.map);
            });
        });

    }
}

init();

})(window, document);
