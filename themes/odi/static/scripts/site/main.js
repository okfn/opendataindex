define(['table', 'place', 'ui', 'domReady', 'sexyTables'], function(table, place, ui, domReady, sexyTables) {
    domReady(function() {
        place.init();
        table.init();
        ui.init();
        sexyTables();
    });
});
