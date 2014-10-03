---

layout: default
key: place
redirect_from: "/historical/2014/"
title:  Places
summary: The Open Data Index ranks governments in terms of the openness of their data. An initiative of Open Knowledge, the leaders in open data.
year: "2014"

---

{% include partials/dataviews/glance.html year=page.year data_glance_class="row" data_point_class="col-md-3" %}

{% include partials/dataviews/comparative_table.html year=page.year %}

<h4>See this data over time</h4>
<ul>
    {% for year in site.odi.years %}
    
    {% if year == site.odi.current_year %}
    {% assign route = page.url %}
    {% assign anchor = "Current" %}
    {% else %}
    {% assign route = site.baseurl | append: "/historical/" | append: year | append: "/" %}
    {% assign anchor = year %}
    {% endif %}
    
    <li>{% include partials/historical_link.html route=route anchor=anchor %}</li>
    {% endfor %}
</ul>
