define(['jquery', 'pubsub'], function($, pubsub) {

    var topics = {
            meta: 'data.meta',
            places: 'data.places',
            datasets: 'data.datasets',
            entries: 'data.entries',
            geo: 'data.geo'
        },
        api = {
            meta: '/api/meta.json',
            places: '/api/places.json',
            datasets: '/api/datasets.json',
            entries: '/api/entries.json',
            geo: '/static/data/world.geo.json'
        };

    function getMetaData() {
        // $.get(api.meta)
        //   .done(function(data) {
        //     pubsub.publish(topics.meta, data);
        // });
        // MOCK
        data = {
            current_year: "2014",
            years: ["2014", "2013"]
        };

        pubsub.publish(topics.meta, data);

    }

    function getPlaceData(callback) {

        $.get(api.places)
          .done(function(data) {
            // callback publishes the places topic
            callback(data);
        });

    }

    function getGeoData(place_data) {
        var d = {};
        $.get(api.geo)
          .done(function(data) {
            // pubsub.publish(topics.geo, data);
            d.places = place_data;
            d.geo = data;
            pubsub.publish(topics.places, d);
        });

    }

    function getDatasetData() {

        $.get(api.datasets)
          .done(function(data) {
            pubsub.publish(topics.datasets, data);
        });

    }

    function getEntryData() {

        $.get(api.entries)
          .done(function(data) {
            pubsub.publish(topics.entries, data);
        });

    }

    function initializeData() {
        getMetaData();
        getPlaceData(getGeoData);
        getDatasetData();
        getEntryData();
    }

    return {
        init: initializeData,
        topics: topics
    };

});



