{{ fullname }}
{{ underline }}

.. automodule:: {{ fullname }}

..
  TODO remove imported members here and below

.. autosummary::
   :nosignatures:

   {{ (functions + classes + exceptions) | sort | join('\n   ') }}

..
  TODO sort according to above summary

{% for x in functions | sort -%}
.. autofunction:: {{ x }}
{% endfor %}
{%- for x in classes | sort -%}
.. autoclass:: {{ x }}
{% endfor %}
{%- for x in exceptions | sort -%}
.. autoexception:: {{ x }}
{% endfor %}
