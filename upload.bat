@ECHO OFF

if "%1" == "release" (
    ECHO Upload to PyPI - NO TEST
    PAUSE
    twine upload --repository pypi dist/ezdxf*
) else (
    ECHO Upload to TestPyPI - TEST
    twine upload --repository testpypi dist/ezdxf*
)
