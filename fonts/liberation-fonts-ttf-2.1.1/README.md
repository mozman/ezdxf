  Liberation Fonts
  =================

  The Liberation Fonts is font collection which aims to provide document 
  layout compatibility as usage of Times New Roman, Arial, Courier New.


  Requirements
  =================

  * [fontforge](http://fontforge.sourceforge.net)
  * [python fonttools](https://pypi.org/project/fonttools/)


 Install
  ============

  1. Get sources

   The latest sources are available via github by checking out the repo:
   
   	$ git clone https://github.com/liberationfonts/liberation-fonts

   Or downloading the tar.gz file via [github](https://github.com/liberationfonts/liberation-fonts/tags).
    eg. 2.00.5 can be retrieved via:
    
	$ wget https://github.com/liberationfonts/liberation-fonts/files/2926169/liberation-fonts-2.00.5.tar.gz

   You can extract the files using the following command where VERSION=2.00.4:
  	
	$ tar zxvf liberation-fonts-[VERSION].tar.gz

  2. Build from the source
  
	$ cd liberation-fonts    or   $ cd liberation-fonts-[VERSION]
	$ make
		
   The binary font files will be available in 'liberation-fonts-ttf-[VERSION]' directory.

  3. Install to system
  
   Fedora Users : 
   One can manually install the fonts by copying the TTFs to `~/.fonts` for user wide usage, 
   and/or to `/usr/share/fonts/liberation` for system-wide availability. 
   Then, run `fc-cache` to let that cached.

   Other distributions : 
   please check out corresponding documentation.


  Usage
  ==========

  Simply select preferred liberation font in applications and start using.


   License
  ============

  This Font Software is licensed under the SIL Open Font License,
  Version 1.1.

  Please read file "LICENSE" for details.


   For Maintainers
  ====================

  Before packaging a new release based on a new source tarball, you have to
  update the version suffix in the Makefile:

    VER = [VERSION]

  Make sure that the defined version corresponds to the font software metadata
  which you can check with ftinfo/otfinfo or fontforge itself. It is highly 
  recommended that file 'ChangeLog' is updated to reflect changes.

  Create a tarball with the following command:

    $ make dist

  The new versioned tarball will be available in the dist/ folder as
  `liberation-fonts-[NEW_VERSION].tar.gz.`

  Credits
 ============

  Please read file "AUTHORS" for list of contributors.
