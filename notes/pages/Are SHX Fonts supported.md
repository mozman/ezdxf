tags:: FAQ

- The SHX font format is not documented nor supported by many libraries/packages like [[Matplotlib]] and [[PyQt]] , therefore only SHX fonts which have corresponding [[TTF]]-fonts can be rendered by these backends.
- Since [[ezdxf]] v1.1 font rendering is done by [[ezdxf]] itself and support for [[SHX]], [[SHP]] and [[LFF]] fonts was added. The directories where these shape fonts are located have to be added to the `support_dirs` in your [[config file]].
	- See also: [[Recognize New Installed Fonts]]