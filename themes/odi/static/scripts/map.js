require.config({
    baseUrl: 'SITEURL/static'.replace('SITEURL', siteUrl),
    shim: {
        leaflet: {
            exports: 'L'
        },
        leaflet_zoommin: {
            deps: ['leaflet']
        }
    },
    paths: {
        app: 'scripts/map/main',
        leaflet: 'vendor/leaflet',
        leaflet_zoommin: 'vendor/L.Control.ZoomMin',
        jquery: 'vendor/jquery.min',
        chroma: 'vendor/chroma.min',
        pubsub: 'vendor/pubsub',
        lodash: 'vendor/lodash.compat.min',
        marked: 'vendor/marked',
        data: 'scripts/map/data',
        ui: 'scripts/map/ui'
    }
});

requirejs(['app']);
