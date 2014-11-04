require.config({
    baseUrl: 'SITEURL/static'.replace('SITEURL', siteUrl),
    paths: {
        app: 'scripts/map/main',
        leaflet: 'vendor/leaflet',
        jquery: 'vendor/jquery.min',
        chroma: 'vendor/chroma.min',
        pubsub: 'vendor/pubsub',
        lodash: 'vendor/lodash.compat.min',
        data: 'scripts/map/data',
        ui: 'scripts/map/ui'
    }
});

requirejs(['app']);
