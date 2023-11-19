alias:: font-cache

- documenation about font caching: <https://ezdxf.mozman.at/docs/tools/fonts.html#font-caching>
- When you install new fonts on your system you have to rebuild the [[font cache]]:
  id:: 6559cccd-b1da-4490-b909-a5cc18d23db7
	- Rebuild the [[font cache]] in a _Python_ script:
	  id:: 6559ccf9-2a1c-4efe-9875-f9a0f5e02b26
	  ```Python
	  import ezdxf
	  from ezdxf.tools import fonts
	  
	  fonts.build_system_font_cache()
	  ```
	- Call the [[ezdxf]] [[launcher]] to rebuild the [[font-cache]]:
	  id:: 6559cd2e-0bf8-4d2d-885b-3c97ae22f381
	  ```shell
	  ezdxf --fonts
	  ```