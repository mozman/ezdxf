## New Requirements
	- This version requires Python 3.8 or newer.
	- The `numpy` and `fontTools` packages are hard dependencies.
	- **WARNING:** The font support has changed drastically in this version. If you directly use the `ezdxf.tools.fonts` module, your code will break. We apologize for the inconvenience. To use the previous version, pin the `ezdxf` version to v1.0.3 in your `requirements.txt` file!
	-
- ## Font Rendering by FontTools
	- Font rendering using `matplotlib` has been replaced by `fontTools`. It is now faster and more accurate. However, the convenient multi-platform support provided by `matplotlib` must now be handled by `ezdxf`, and it may not work as smoothly as with `matplotlib`.
	- The available fonts on a system are cached in the `$XDG_CACHE_HOME/ezdxf` directory, which defaults to `~/.cache/ezdxf`. Please note that this cache will **not** be updated automatically if you add or remove fonts.
	- To update the font cache, use the following command:
	  ```shell
	  ezdxf --fonts
	  ```
	- For more information on this topic, please refer to [this link](https://ezdxf.mozman.at/docs/howto/fonts.html).
	-
- ## Shape Font Support
	- We've added new support for measuring and rendering `.shx`, `.shp`, and `.lff` fonts.
	- Shape fonts are the basic stroke fonts commonly found in CAD applications. None of these fonts are included in `ezdxf` due to licensing restrictions or the restrictive licensing of the `.lff` fonts used in LibreCAD.
	- As there is no universal way to find these fonts, you will need to create a config file and add the font directories where these fonts are located to the `support_dirs` entry.
	- For more information on config files, please read [this link](https://ezdxf.mozman.at/docs/options.html#config-files).
	- On Linux, you can add symbolic links to these directories in the `~/.fonts` directory.
	- Don't forget to update the font cache when adding new font directories!
	-
- ## New Backends for the Drawing Add-on
	- We've introduced new backends to the `drawing` add-on, allowing you to export DXF content as SVG, PDF, PNG, PLT/HPGL2, and simplified DXF files.
	- The new SVG backend is a native implementation and does not require the `matplotlib` package. It creates smaller files and supports the new page layout features introduced in this version.
	- The new PDF and PNG backends require the `PyMuPdf` package, offering faster rendering and support for the new page layout features compared to the `matplotlib` package.
	- The PLT/HPGL2 backend creates plot files for raster plotters. It's a native implementation and does not require additional packages. **CAUTION:** The output of this backend is only tested with a plot file viewer and not on real hardware!
	- The DXF backend creates a flattened DXF file with only these DXF primitives:
		- POINT
		- LINE
		- LWPOLYLINE
		- SPLINE
		- HATCH.
	- We've added a new [tutorial](https://ezdxf.mozman.at/docs/tutorials/image_export.html) for using these new backends and the new page layout features.
	-
- ## New Hpgl2 Add-on
	- The `hpgl2` add-on provides tools to process and convert HPGL/2 plot files. You can use the `hpgl` command in the launcher to view and convert plot files via a PyQt GUI:
	  
	  ```shell
	  ezdxf hpgl
	  ```
	- For more information, please refer to the [docs](https://ezdxf.mozman.at/docs/addons/hpgl2.html).
	-
- ## New ezdxf.xref Module
	- We've introduced a new `ezdxf.xref` module to improve the handling of external references and the import of resources. This module serves as a replacement for the `Importer` add-on but has a completely different API.
	- For more information, please read the [docs](https://ezdxf.mozman.at/docs/xref.html) and the new [tutorial](https://ezdxf.mozman.at/docs/tutorials/xref_module.html).
	- If you have any comments, ideas, or suggestions, please feel free to post them in the [discussion forum](https://github.com/mozman/ezdxf/discussions) on GitHub.
	-
- ### See you sometime, take care, stay healthy!