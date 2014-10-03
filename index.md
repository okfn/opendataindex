---

layout: default
key: home
title:  Open Data Index
year: "2014"

---

{% capture home_intro %}{% include content/home_intro.md %}{% endcapture %}
{{ home_intro|markdownify }}

{% include partials/dataviews/glance.html year=page.year data_glance_class="row" data_point_class="col-md-3" %}

{% include partials/dataviews/comparative_table.html year=page.year %}

Previous Years: <a href="{{ site.baseurl }}/historical/2013/" title="">2013</a>

