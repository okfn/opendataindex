define(['leaflet', 'jquery', 'pubsub', 'lodash', 'chroma', 'data'], function(leaflet, $, pubsub, _, chroma, data) {

    var $tools = $('.odi-visualisation-tools'),
        $legend = $('.odi-visualisation-legend-key ul'),
        $display = $('.odi-visualisation-display'),
        $embedTrigger = $('.odi-visualisation-embed-toggle'),
        $embedModal = $('.odi-visualisation-embed-iframe'),
        $legendExplanationTrigger = $('.odi-visualisation-legend-explanation-toggle'),
        $legendExplanationModal = $('.odi-visualisation-legend-explanation'),
        $datasetFilter = $tools.find('.odi-filter-dataset').first(),
        $yearFilter = $tools.find('.odi-filter-year').first(),
        colorBoundaries = ['#dd3d3a', '#8bdd3a'],
        colorScale = chroma.scale(colorBoundaries).domain([0, 100]),
        mapTileLayer = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        map = L.map('map').setView([20.0, 5.0], 2),
        placeInfo = L.control(),
        placeInfoTmpl = '<div class="odi-visualisation-place-information-name">NAME</div><div class="odi-visualisation-place-information-title">Open Data Index YEAR</div><div class="odi-visualisation-place-information-text"><ul><li><span class="label">Score</span>SCORE%</li><li><span class="label">Rank</span> #RANK</li></ul><a href="/places/SLUG/" title="More information about NAME in the YEAR Open Data Index">More information</a></div>',
        queryString = window.location.search,
        topics = {
            init: 'init',
            tool_change: 'tool.change',
            data_slice_change: 'data_slice.change'
        },
        dataSlice = setDataSlice(topics.init, getArgsFromWindow()),
        geojson,
        meta,
        places,
        datasets,
        entries,
        geo;

    pubsub.subscribe(data.topics.meta, metaHandler);
    pubsub.subscribe(data.topics.places, placeHandler);
    pubsub.subscribe(data.topics.datasets, datasetHandler);
    pubsub.subscribe(data.topics.entries, entryHandler);
    pubsub.subscribe(topics.tool_change, setDataSlice);
    pubsub.subscribe(topics.data_slice_change, redrawDisplay);

    function setDataSlice(topic, data) {

        var sliceargs = {
                year: undefined,
                dataset: undefined
        };

        _.each(sliceargs, function(value, key) {
            _.forOwn(data, function(value, key) {
                if (_.has(sliceargs, key)) {
                    sliceargs[key] = value;
                }
            });
        });

        dataSlice = sliceargs;
        pubsub.publish(topics.data_slice_change, sliceargs);
        return dataSlice;

    }

    function getArgsFromWindow() {

        var cleaned = queryString
                    .replace(/\?/g, '')
                    .replace(/\//g, '')
                    .split("&"),
            args = {};

        _.each(cleaned, function(value) {
            tmp = value.split('=');
            args[tmp[0]] = tmp[1];
        });

        return args;

    }

    function setPlaceColors(feature) {

        var fillColor = '#f5f5f5',
        score = 0,
        match;

        if (dataSlice.dataset === 'all' ||
            typeof(dataSlice) === 'undefined' ||
            typeof(dataSlice.dataset) === 'undefined') {

            // get calculated total scores from the place data
            match = _.find(places, {'id': feature.properties.iso_a2});

            if (match) {
                score = parseInt(match.score, 10);
                fillColor = colorScale(score).hex();
            }

        } else {

            // calculate for this dataset/year/place from entries data
            match = _.find(entries, {
                'place': feature.properties.iso_a2,
                'year': dataSlice.year,
                'dataset': dataSlice.dataset
            });

            if (match) {
                score = parseInt(match.score, 10);
                fillColor = colorScale(score).hex();
            }

        }

        return {
                fillColor: fillColor,
                weight: 1,
                opacity: 1,
                color: '#6f6c75',
                dashArray: '2',
                fillOpacity: 0.5
        };

    }

    function placeHoverHandler(e) {

        var layer = e.target;

        layer.setStyle({
            weight: 3,
            color: '#605d65',
            dashArray: '',
            fillOpacity: 0.5
        });

        if (!L.Browser.ie && !L.Browser.opera) {
            layer.bringToFront();
        }

        placeInfo.update(layer.feature.properties);

    }

    function placeExitHandler(e) {

        geojson.resetStyle(e.target);
        // we want to leave the display until next place hover
        //placeInfo.update();

    }

    function placeClickHandler(e) {

        map.fitBounds(e.target.getBounds());

    }

    function setGeoColorScale(geo) {

        // Consider without tiles? Looks better IMHO.
        // L.tileLayer(mapTileLayer).addTo(map);
        geojson = L.geoJson(geo, {
            style: setPlaceColors,
            onEachFeature: onEachPlace
        }).addTo(map);

    }

    function onEachPlace(feature, layer) {

        layer.on({
            mouseover: placeHoverHandler,
            mouseout: placeExitHandler,
            click: placeClickHandler
        });

    }

    function metaHandler(topic, data) {

        meta = data;

        _.each(data.years, function(value) {
            tmpl = '<option value="YEAR" SEL>YEAR</option>'
                     .replace(/YEAR/g, value);

            if (dataSlice.year === value) {
                tmpl = tmpl.replace('SEL', 'selected');
            } else {
                tmpl = tmpl.replace('SEL', '');
            }

            $yearFilter.append(tmpl);
        });

    }

    function placeHandler(topic, data) {

        places = data.places;
        geo = data.geo;
        geoHandler(geo);

    }

    function geoHandler(data) {

        setGeoColorScale(data);

    }

    function datasetHandler(topic, data) {

        datasets = data;

        _.each(data, function(value) {
            tmpl = '<option value="ID" SEL>NAME</option>'
                     .replace('ID', value.id)
                     .replace('NAME', value.title);

            if (dataSlice.dataset === value.id) {
                tmpl = tmpl.replace('SEL', 'selected');
            } else {
                tmpl = tmpl.replace('SEL', '');
            }

            $datasetFilter.append(tmpl);
        });

    }

    function entryHandler(topic, data) {

        entries = data;

    }

    function initializeLegend() {

        $legendExplanationTrigger.on('click', function() {
            $legendExplanationModal.toggle();
        });

        _.each($legend.find('li'), function(value) {
            var $this = $(value);
            var score = parseInt($this.data('score'), 10);
            $this.css('background-color', colorScale(score).hex());
        });

    }

    function initializeShare() {

        $embedTrigger.on('click', function() {
            $embedModal.toggle();
        });

    }

    function initializeTools() {

        var data = {};

        $datasetFilter.on('change', function() {
            data.dataset = $(this).val();
            data.year = $yearFilter.val();
            pubsub.publish(topics.tool_change, data);
        });

        $yearFilter.on('change', function() {
            data.year = $(this).val();
            data.dataset = $datasetFilter.val();
            pubsub.publish(topics.tool_change, data);
        });

    }

    function redrawDisplay(topic, data) {

        setGeoColorScale(geo);

    }

    function initializeDisplay() {

        placeInfo.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'odi-visualisation-place-information'); // create a div with a class "info"
            this.update();
            return this._div;
        };

        placeInfo.update = function (properties) {
            var score,
                rank,
                year,
                match,
                rendered_tmpl = placeInfoTmpl;

            if (properties) {
                match = _.find(places, {'id': properties.iso_a2});
                score = parseInt(match.score, 10);
                rank = parseInt(match.rank, 10);
                rendered_tmpl = placeInfoTmpl
                                  .replace(/YEAR/g, year || '2014')
                                  .replace(/NAME/g, match.name)
                                  .replace(/SLUG/g, match.slug)
                                  .replace(/SCORE/g, score)
                                  .replace(/RANK/g, rank);
            } else {
                rendered_tmpl = 'Hover on a place';
            }
            this._div.innerHTML = rendered_tmpl;
        };

        placeInfo.addTo(map);

    }

    function initializeUI() {
        initializeLegend();
        initializeShare();
        initializeDisplay();
        initializeTools();

    }

    return {
        init: initializeUI
    };

});

