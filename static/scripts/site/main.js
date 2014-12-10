define(['table', 'place', 'ui', 'domReady'], function(table, place, ui, domReady) {
    domReady(function() {
        place.init();
        table.init();
        ui.init();
    });
});
