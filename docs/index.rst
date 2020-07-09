Run Panel
---------

Simple example of animation in Qt app.

Features
========

- Launch panel for any application or command

- Auto hide when lose focus and auto pop up on cursor hover

- Customizable by JSON file

Config files
============

You can configure panel with config files:

buttons.json
~~~~~~~~~~~~

Add file ``buttons.json`` to folder ``settings`` and write config for your apps.
Use file ``buttons_example.json`` as reference.

**.../run_panel/settings/buttons.json**

.. code-block:: json

    [
        "my_app": {
            "tooltip": "My App",
            "icon": "app.png",
            "commands": [
                    {
                        "title": "MyApp",
                        "executable": "/path/to/executable",
                        "args": [],
                        "env": {}
                    }
            ]
        }
    ]

custom_ui.json
~~~~~~~~~~~~~~

This file can change panel settings. Create file ``custom_ui.json`` in ``settings`` folder and override what you want.

**.../run_panel/settings/buttons.json**

.. code-block::

    {
        "hide_timeout": 5000
    }

custom_style.qss
~~~~~~~~~~~~~~~~

You can change default style with file ``custom_style.qss``

**.../run_panel/res/custom_style.qss**

.. code-block:: css

    QPushButton:hover
    {
        border: none;
        background-color: gray;
    }