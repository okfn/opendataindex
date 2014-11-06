define(['leaflet', 'jquery', 'pubsub', 'lodash', 'chroma', 'marked', 'data'], function(leaflet, $, pubsub, _, chroma, marked, data) {

    var $tools = $('.odi-vis-tools'),
        $legend = $('.odi-vis-legend ul'),
        $display = $('.odi-vis-display'),
        $infoTrigger = $('.odi-vis-show-info'),
        $infoBox = $('.odi-vis-info'),
        $infoClose = $('.odi-vis-info-close'),
        $placeBox = $('.odi-vis-place'),
        $placeClose = $('.odi-vis-place-close'),
        $datasetFilter = $tools.find('.odi-filter-dataset').first(),
        $yearFilter = $tools.find('.odi-filter-year').first(),
        colorLight = '#f5f5f5',
        colorDark = '#2d2d2d',
        colorSteps = ['#ff0000', '#edcf3b', '#7ab800'],
        colorScale = chroma.scale(colorSteps).domain([0, 100]),
        mapInitObj = {
            zoomControl: false,
            attributionControl: false
        },
        map = leaflet.map('map', mapInitObj).setView([20.0, 5.0], 2),
        placeControl = leaflet.control(),
        placeBoxClass = 'odi-vis-place',
        placeBoxTmpl = _.template($('script.place-box').html()),
        placeStyleBase = {
            weight: 1,
            opacity: 1,
            color: colorDark,
            dashArray: '2',
            fillOpacity: 1
        },
        placeStyleFocus = {
            weight: 1.5,
            color: colorDark,
            dashArray: '',
        },
        infoBoxTmpl = _.template($('script.info-box').html()),
        embedCode = $('.odi-vis-info-iframe-code').html(),
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
        var fillColor = colorLight,
        score = 0,
        match;

        if (dataSlice.dataset === 'all' ||
            typeof(dataSlice) === 'undefined' ||
            typeof(dataSlice.dataset) === 'undefined') {

            // get calculated total scores from the place data
            match = _.find(places, {'id': feature.properties.iso_a2.toLowerCase()});

            if (match) {
                score = parseInt(match.score, 10);
                fillColor = colorScale(score).hex();
            }

        } else {

            // calculate for this dataset/year/place from entries data
            match = _.find(entries, {
                'place': feature.properties.iso_a2.toLowerCase(),
                'year': dataSlice.year,
                'dataset': dataSlice.dataset
            });

            if (match) {
                score = parseInt(match.score, 10);
                fillColor = colorScale(score).hex();
            }

        }
        rv = _.clone(placeStyleBase);
        rv.fillColor = fillColor;
        return rv;
    }

    function placeHoverHandler(event) {
        var layer = event.target;

        layer.setStyle(placeStyleFocus);
        if (!leaflet.Browser.ie && !leaflet.Browser.opera) {
            layer.bringToFront();
        }
    }

    function placeExitHandler(event) {
        geojson.resetStyle(event.target);
    }

    function placeClickHandler(event) {
        map.fitBounds(event.target.getBounds());
        placeControl.update(event.target.feature.properties);
    }

    function setGeoColorScale(geo) {
        geojson = leaflet.geoJson(geo, {
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

    function redrawDisplay(topic, data) {
        setGeoColorScale(geo);
    }

    /**
     * Bootstraps listeners for the info panel
     */
     function initMetaInfo() {
        var $this,
            embedClass = 'odi-vis-embed',
            context = {},
            activeInfo = '_activeinfo';

        $infoClose.on('click', function() {
            console.log('BOOM');
            $infoBox.empty();
            $infoBox.hide();
        });

        $infoTrigger.on('click', function() {
            $this = $(this);
            if ($this.hasClass(activeInfo)) {
                $this.removeClass(activeInfo);
                $infoBox.empty();
                $infoBox.hide();
            } else {
                context.title = $this.data('title');
                context.text = marked($this.data('text'));
                if ($this.hasClass(embedClass)) {
                    context.embed_code = embedCode;
                } else {
                    context.embed_code = '';
                }
                $this.siblings().removeClass(activeInfo);
                $this.addClass(activeInfo);
                $infoBox.html(infoBoxTmpl(context));
                $infoBox.show();
            }
        });
     }

    /**
     * Bootstraps visualisation tools
     */
    function initMetaTools() {
        var $this,
            data = {};

        $datasetFilter.on('change', function() {
            $this = $(this);
            data.dataset = $this.val();
            data.year = $yearFilter.val();
            pubsub.publish(topics.tool_change, data);
        });

        $yearFilter.on('change', function() {
            $this = $(this);
            data.year = $this.val();
            data.dataset = $datasetFilter.val();
            pubsub.publish(topics.tool_change, data);
        });
    }

    /**
     * Bootstraps visualisation legend
     */
    function initMetaLegend() {
        var $this,
            score;

        _.each($legend.find('li'), function(value) {
            $this = $(value);
            score = parseInt($this.data('score'), 10);
            $this.css('background-color', colorScale(score).hex());
        });
    }

    /**
     * Bootstraps the visualisation meta section
     */
    function initMeta() {
        initMetaTools();
        initMetaLegend();
        initMetaInfo();
    }

    /**
     * Bootstraps the visualisation place box, which displays data on places
     */
    function initViewPlaceBox() {
        placeControl.onAdd = function (map) {
            this._div = leaflet.DomUtil.create('div', placeBoxClass);
            this.update();
            return this._div;
        };

        placeControl.update = function (properties) {
            var context = {},
                match;

            if (properties) {
                match = _.find(places, {'id': properties.iso_a2.toLowerCase()});
                context.year = '2014';
                context.name = match.name;
                context.slug = match.id;
                context.score = parseInt(match.score, 10);
                context.rank = parseInt(match.rank, 10);
                context.improvement_phrase = 'an improvment on';
                context.previous_score = '50';
                $placeBox.html(placeBoxTmpl(context));
                $placeBox.show();
            }
        };
    }

    /**
     * Bootstraps the visualisation map
     */
    function initViewMap() {
        new leaflet.Control.Zoom({ position: 'bottomright' }).addTo(map);
    }

    /**
     * Bootstraps the visualisation view section
     */
    function initView() {
        initViewMap();
        initViewPlaceBox();
    }

    /**
     * Boostraps the visualisation interface
     */
    function initUI() {
        initMeta();
        initView();
    }

    return {
        init: initUI
    };

});

