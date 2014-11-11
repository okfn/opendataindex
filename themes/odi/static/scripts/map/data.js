define(['jquery', 'pubsub'], function($, pubsub) {

    var topics = {
            meta: 'data.meta',
            summary: 'data.summary',
            places: 'data.places',
            datasets: 'data.datasets',
            entries: 'data.entries',
            geo: 'data.geo'
        },
        api = {
            summary: 'SITEURL/api/summary.json'.replace('SITEURL', siteUrl),
            places: 'SITEURL/api/places.json'.replace('SITEURL', siteUrl),
            datasets: 'SITEURL/api/datasets.json'.replace('SITEURL', siteUrl),
            entries: 'SITEURL/api/entries.json'.replace('SITEURL', siteUrl),
            geo: 'SITEURL/static/data/world.geo.json'.replace('SITEURL', siteUrl)
        };

    /**
     * Gets meta data and publishes topic when ready
     */
    function getMetaData() {
        data = {
            currentYear: currentYear,
            years: years
        };
        pubsub.publish(topics.meta, data);
    }

    /**
     * Gets summary data and publishes topic when ready
     */
    function getSummaryData() {
        $.get(api.summary)
          .done(function(data) {
            pubsub.publish(topics.summary, data);
        });
    }

    /**
     * Gets place data and passes to `callback` for further processing
     */
    function getPlaceData(callback) {
        $.get(api.places)
          .done(function(data) {
            // callback publishes the places topic
            callback(data);
        });
    }

    /**
     * Gets geo data from the available places and publishes topic when ready
     */
    function getGeoData(place_data) {
        var d = {};
        $.get(api.geo)
          .done(function(data) {
            d.places = place_data;

            // add centroid to properies of each feature
            _.each(data.features, function(value) {
                if (value.geometry.type === 'Polygon') {
                    value.properties.centroid = getCentroidFromPolygon(
                        value.geometry.coordinates);
                } else {
                    value.properties.centroid = getCentroidFromPolygon(
                        value.geometry.coordinates[0]);
                }
            });

            d.geo = data;
            pubsub.publish(topics.places, d);
        });

    }

    /**
     * Gets dataset data and publishes topic when ready
     */
    function getDatasetData() {
        $.get(api.datasets)
          .done(function(data) {
            pubsub.publish(topics.datasets, data);
        });
    }

    /**
     * Gets entry data and publishes topic when ready
     */
    function getEntryData() {
        $.get(api.entries)
          .done(function(data) {
            pubsub.publish(topics.entries, data);
        });
    }

    /**
     * Bootstraps the data required for the visualisation
     */
    function initData() {
        getMetaData();
        getPlaceData(getGeoData);
        getDatasetData();
        getEntryData();
    }

    function getCentroidFromPolygon(polygon) {
        // adapted from Leaflet's getCenter
        var i, j, len, p1, p2, f, area, x, y,
            points = polygon[0];

        area = x = y = 0;

        for (i = 0, len = points.length, j = len - 1; i < len; j = i++) {
                p1 = points[i];
                p2 = points[j];
                f = p1[1] * p2[0] - p2[1] * p1[0];
                x += (p1[0] + p2[0]) * f;
                y += (p1[1] + p2[1]) * f;
                area += f * 3;
        }
        return [x / area, y / area];
    }

    return {
        init: initData,
        topics: topics
    };

});



