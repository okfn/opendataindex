---

layout: default
key: home
redirect_from: "/historical/2014/"
title:  Open Data Index

---

{% capture home_intro %}{% include content/home_intro.md %}{% endcapture %}
{{ home_intro|markdownify }}

{% include partials/data_glance.html year="2014" data_glance_class="row" data_point_class="col-md-3" %}

{% include partials/data_table.html year="2014" %}

Previous Years: <a href="/historical/2013/" title="">2013</a>

