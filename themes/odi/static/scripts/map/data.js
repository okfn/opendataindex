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
            previousYear: previousYear,
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

    return {
        init: initData,
        topics: topics
    };
});



