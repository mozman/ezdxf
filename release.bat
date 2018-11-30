@ECHO OFF
ECHO Upload to PyPI - NO TEST
PAUSE
twine upload --repository pypi dist/ezdxf*
mv -f dist/ezdxf* dist/archiv
