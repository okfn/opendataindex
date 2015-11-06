require.config({
    baseUrl: 'SITEURL/static'.replace('SITEURL', siteUrl),
    shim : {
        bootstrap: {deps:['jquery']},
        tablesorter: {deps: ['jquery']},
        stickykit: {deps: ['jquery']},
        kinetic: {deps: ['jquery']},
        sexyTables: {deps: ['kinetic']}
    },
    paths: {
        app: 'scripts/site/main',
        domReady: 'vendor/domReady',
        jquery: 'vendor/jquery.min',
        tablesorter: 'vendor/jquery.tablesorter.min',
        stickykit: 'vendor/jquery.sticky-kit.min',
        bootstrap: 'vendor/bootstrap/js/bootstrap.min',
        chroma: 'vendor/chroma.min',
        lodash: 'vendor/lodash.compat.min',
        table: 'scripts/site/table',
        place: 'scripts/site/place',
        ui: 'scripts/site/ui',
        kinetic: 'vendor/jquery.kinetic.min',
        sexyTables: 'vendor/sexytables-1.0.min'
    }
});

requirejs(['app']);
