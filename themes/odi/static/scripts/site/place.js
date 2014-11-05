define(['jquery', 'bootstrap', 'chroma'], function($, bootstrap, chroma) {

    var colorBoundaries = ['#ff0000', '#7AB800'],
        colorScale = chroma.scale(colorBoundaries).domain([0, 100]),
        $placeOpeness = $('.place-openness'),
        naString = 'n/a',
        score;

    function initializePlace() {

        $.each($placeOpeness, function(index, el) {
            var $el = $(el);
            if ($el.data('score') === naString) {
                score = 0;
            } else {
                score = parseInt($el.data('score'), 10);
            }
            $el.css({
              'background-color': colorScale(score).hex(),
              'color': 'white'
            });
        });

    }

    return {
        init: initializePlace,
    };

});
