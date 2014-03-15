---
layout: default
title: Home
tagline: Try Work Smart
---
{% include JB/setup %}


{% for post in site.posts %}
  <hr>
  <h5><span>{{ post.date | date_to_string }}</span> &raquo; <a href="{{ BASE_PATH }}{{ post.url }}">{{ post.title }}</a></h5>  
  {{post.description}}
  {% if post.figure %}
<a href="{{post.url}}"><img src="{{post.figure}}"/></a>
  {% endif %}
{% endfor %}
