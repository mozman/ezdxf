@ECHO OFF
ECHO TEST TEST TEST - upload to TestPyPI - TEST TEST TEST
twine upload --repository testpypi dist/ezdxf*
mv -f dist/ezdxf* dist/archiv