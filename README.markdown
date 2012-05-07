This is an attempt to improve
http://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/ext/ereporter/
See https://github.com/mdornseif/my_ereporter for further Information.

To use:

    mkdir -P lib
    git submodule add git@github.com:mdornseif/my_ereporter.git lib/my_ereporter
    echo "import os.path" > lib/__init__.py
    echo "import site" >> lib/__init__.py
    echo "site.addsitedir(os.path.dirname(__file__))" >> lib/__init__.py
    echo "./my_ereporter" >> lib/submodules.pth


In `app.yaml`:

    handlers:
    - url: /_ereporter/display.html
      script: lib/my_ereporter/myereporter/report_display.py
      login: admin

    - url: /_ereporter.*
      script: lib/my_ereporter/myereporter/report_generator.py
      login: admin



Then in your `main.py`:

    import myereporter
    # Problem: eReporter does not support exceptions in transactions
    # http://code.google.com/p/googleappengine/issues/detail?id=5220
    myereporter.register_logger()
