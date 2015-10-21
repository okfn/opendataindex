require.config({
    baseUrl: 'SITEURL/static'.replace('SITEURL', siteUrl),
    shim: {
        leaflet: {exports: 'L'},
        leaflet_zoommin: {deps: ['leaflet']},
        leaflet_label: {deps: ['leaflet']}
    },
    paths: {
        app: 'scripts/map/main',
        domReady: 'vendor/domReady',
        leaflet: 'vendor/leaflet',
        proj4: 'vendor/proj4',
        proj4leaflet: 'vendor/proj4leaflet',
        leaflet_zoommin: 'vendor/L.Control.ZoomMin',
        leaflet_label: 'vendor/leaflet.label',
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
