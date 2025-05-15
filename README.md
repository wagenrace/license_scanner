# license_scanner

[![Downloads](https://static.pepy.tech/badge/license-scanner)](https://pepy.tech/project/license-scanner)

Find all licenses needed by the package in your python environment.
It will sort all package by license.

Install by pip

```cmd
pip install license_scanner
```

Usage

```cmd
license_scanner
```

![](readme_files/demo.gif)

## Check within you pipeline

You can make your pipeline fail if a project does not have the correct licenses.
To do so create a `pyproject.toml` and add underneath `tool.license_scanner` two lists `allowed-licenses` and `allowed-packages`.
If a package does not have license in `allowed-licenses` AND it is not in `allowed-packages` it will throw an error.

```toml
[tool.license_scanner]
allowed-licenses = [
  "MIT",
  "apache software license",
  "apache software license v2",
  "apache software license v3",
  "BSD license",
  "BSD 3-clause license",
  'GNU lesser general public license',
  'GNU lesser general public license v2',
  'GNU lesser general public license v3',
  'Python software foundation license',
  'Mozilla public license 2.0 (mpl 2.0)',
  'mozilla',
]
allowed-packages = ["license_scanner"]
```

To run the license scanner make sure you are in the same directory as `pyproject.toml` and run `license_scanner -m whitelist` or `python -m license_scanner -m whitelist`. 
It will now throw you an error if your environment has an package with a license you did not approve of.

### Example: Github actions

This github actions triggers every time you make a PR to the main branch. With `pip install .` it installs the current project, next it installs `license_scanner`, and lastly it runs the check.

Be aware, if you want to do unittest make sure you install `pytest` AFTER you run license_scanner. Otherwise `pytest` is in your environment when you check for unwanted licenses.

```yaml
name: Licenses check

on:
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  deploy:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.x'
    - name: Check for licenses
      run: |
        python -m pip install --upgrade pip
        pip install .
        pip install license_scanner
        python -m license_scanner -m whitelist

```

## Supported licenses

- Abstyles License
- academic free license v1.1
- academic free license v1.2
- academic free license v2.0
- academic free license v2.1
- academic free license v3.0
- Academy of Motion Picture Arts and Sciences BSD
- AdaCore Doc License
- Adaptive Public License 1.0
- Adobe Display PostScript License
- Adobe Glyph List License
- Adobe Postscript AFM License
- Adobe Systems Incorporated Source Code License Agreement
- Adobe Utopia Font License
- Afmparse License
- Aladdin Free Public License
- Amazon Digital Services License
- AMD newlib License
- AMD's plpa_map.c License
- AML glslang variant License
- ANTLR Software Rights Notice
- ANTLR Software Rights Notice with license fallback
- Any OSI License
- Any OSI License - Perl Modules
- Apache license
- Apache License 1.1
- Apache license 1.0
- Apache license 2.0
- App::s2p License
- Apple MIT License
- Apple Public Source License 1.0
- Apple Public Source License 1.1
- Apple Public Source License 1.2
- Apple Public Source License 2.0
- Arphic Public License
- Artistic License 1.0
- Artistic License 1.0 (Perl)
- Artistic License 1.0 w/clause 8
- Artistic License 2.0
- ASWF Digital Assets License 1.1
- ASWF Digital Assets License version 1.0
- Attribution Assurance License
- Azure License
- Baekmuk License
- Bahyph License
- Barr License
- bcrypt Solar Designer License
- Beerware License
- Bitstream Charter Font License
- Bitstream Vera Font License
- BitTorrent Open Source License v1.0
- BitTorrent Open Source License v1.1
- Blue Oak Model License 1.0.0
- Boehm-Demers-Weiser GC License
- Boehm-Demers-Weiser GC License (without fee)
- Boost Software License 1.0
- Borceux license
- Brian Gladman 2-Clause License
- Brian Gladman 3-Clause License
- BSD 1-Clause License
- BSD 2-Clause - first lines requirement
- BSD 2-Clause - Ian Darwin variant
- BSD 2-Clause FreeBSD License
- BSD 2-Clause NetBSD License
- BSD-2-Clause Plus Patent License
- BSD 2-Clause "Simplified" License
- BSD 2-Clause with views sentence
- BSD 3-Clause acpica variant
- BSD 3-Clause Clear License
- BSD 3-Clause Flex variant
- BSD 3-Clause Modification
- BSD 3-Clause "New" or "Revised" License
- BSD 3-Clause No Military License
- BSD 3-Clause No Nuclear License
- BSD 3-Clause No Nuclear License 2014
- BSD 3-Clause No Nuclear Warranty
- BSD 3-Clause Open MPI variant
- BSD 3-Clause Sun Microsystems
- BSD 4.3 RENO License
- BSD 4.3 TAHOE License
- BSD 4-Clause "Original" or "Old" License
- BSD 4 Clause Shortened
- BSD-4-Clause (University of California-Specific)
- BSD Advertising Acknowledgement License
- BSD-Inferno-Nettverk
- BSD license
- BSD 0-clause license
- BSD 2-clause license
- BSD 3-clause license
- BSD 4-clause license
- BSD Protection License
- BSD Source Code Attribution
- BSD Source Code Attribution - beginning of file variant
- BSD with attribution
- BSD with Attribution and HPND disclaimer
- Business Source License 1.1
- bzip2 and libbzip2 License v1.0.5
- bzip2 and libbzip2 License v1.0.6
- Caldera License
- Caldera License (without preamble)
- Catharon License
- Creative Commons Zero, CC-0
- CeCILL-B Free Software License Agreement
- CeCILL-C Free Software License Agreement
- CeCILL Free Software License Agreement v1.0
- CeCILL Free Software License Agreement v1.1
- CeCILL Free Software License Agreement v2.0
- CeCILL Free Software License Agreement v2.1
- CERN Open Hardware Licence v1.1
- CERN Open Hardware Licence v1.2
- CERN Open Hardware Licence Version 2 - Permissive
- CERN Open Hardware Licence Version 2 - Strongly Reciprocal
- CERN Open Hardware Licence Version 2 - Weakly Reciprocal
- CFITSIO License
- check-cvs License
- Checkmk License
- Clarified Artistic License
- Clips License
- CMU Mach - no notices-in-documentation variant
- CMU Mach License
- CNRI Jython License
- CNRI Python License
- CNRI Python Open Source GPL Compatible License Agreement
- Code Project Open License 1.02
- Common Development and Distribution License 1.0
- Common Development and Distribution License 1.1
- Common Documentation License 1.0
- Common Lisp LOOP License
- Common Public Attribution License 1.0
- Common Public License 1.0
- Common Vulnerability Enumeration ToU License
- Community Data License Agreement Permissive 1.0
- Community Data License Agreement Permissive 2.0
- Community Data License Agreement Sharing 1.0
- Community Specification License 1.0
- Computational Use of Data Agreement v1.0
- Computer Associates Trusted Open Source License 1.1
- Condor Public License v1.1
- Copyfree Open Innovation License
- copyleft-next 0.3.0
- copyleft-next 0.3.1
- Cornell Lossless JPEG License
- Creative Commons Attribution 1.0 Generic
- Creative Commons Attribution 2.0 Generic
- Creative Commons Attribution 2.5 Australia
- Creative Commons Attribution 2.5 Generic
- Creative Commons Attribution 3.0 Australia
- Creative Commons Attribution 3.0 Austria
- Creative Commons Attribution 3.0 Germany
- Creative Commons Attribution 3.0 IGO
- Creative Commons Attribution 3.0 Netherlands
- Creative Commons Attribution 3.0 United States
- Creative Commons Attribution 3.0 Unported
- Creative Commons Attribution 4.0 International
- Creative Commons Attribution No Derivatives 1.0 Generic
- Creative Commons Attribution No Derivatives 2.0 Generic
- Creative Commons Attribution No Derivatives 2.5 Generic
- Creative Commons Attribution No Derivatives 3.0 Germany
- Creative Commons Attribution No Derivatives 3.0 Unported
- Creative Commons Attribution No Derivatives 4.0 International
- Creative Commons Attribution Non Commercial 1.0 Generic
- Creative Commons Attribution Non Commercial 2.0 Generic
- Creative Commons Attribution Non Commercial 2.5 Generic
- Creative Commons Attribution Non Commercial 3.0 Germany
- Creative Commons Attribution Non Commercial 3.0 Unported
- Creative Commons Attribution Non Commercial 4.0 International
- Creative Commons Attribution Non Commercial No Derivatives 1.0 Generic
- Creative Commons Attribution Non Commercial No Derivatives 2.0 Generic
- Creative Commons Attribution Non Commercial No Derivatives 2.5 Generic
- Creative Commons Attribution Non Commercial No Derivatives 3.0 Germany
- Creative Commons Attribution Non Commercial No Derivatives 3.0 IGO
- Creative Commons Attribution Non Commercial No Derivatives 3.0 Unported
- Creative Commons Attribution Non Commercial No Derivatives 4.0 International
- Creative Commons Attribution Non Commercial Share Alike 1.0 Generic
- Creative Commons Attribution Non Commercial Share Alike 2.0 England and Wales
- Creative Commons Attribution Non Commercial Share Alike 2.0 Generic
- Creative Commons Attribution Non Commercial Share Alike 2.0 Germany
- Creative Commons Attribution Non Commercial Share Alike 2.5 Generic
- Creative Commons Attribution Non Commercial Share Alike 3.0 Germany
- Creative Commons Attribution Non Commercial Share Alike 3.0 IGO
- Creative Commons Attribution Non Commercial Share Alike 3.0 Unported
- Creative Commons Attribution Non Commercial Share Alike 4.0 International
- Creative Commons Attribution-NonCommercial-ShareAlike 2.0 France
- Creative Commons Attribution Share Alike 1.0 Generic
- Creative Commons Attribution Share Alike 2.0 England and Wales
- Creative Commons Attribution Share Alike 2.0 Generic
- Creative Commons Attribution Share Alike 2.1 Japan
- Creative Commons Attribution Share Alike 2.5 Generic
- Creative Commons Attribution Share Alike 3.0 Austria
- Creative Commons Attribution Share Alike 3.0 Germany
- Creative Commons Attribution Share Alike 3.0 Unported
- Creative Commons Attribution Share Alike 4.0 International
- Creative Commons Attribution-ShareAlike 3.0 IGO
- Creative Commons Public Domain Dedication and Certification
- Creative Commons Public Domain Mark 1.0 Universal
- Creative Commons Share Alike 1.0 Generic
- Creative Commons Zero v1.0 Universal
- Cronyx License
- Crossword License
- Cryptographic Autonomy License 1.0
- Cryptographic Autonomy License 1.0 (Combined Work Exception)
- CrystalStacker License
- CUA Office Public License v1.0
- Cube License
- curl License
- Data licence Germany attribution version 2.0
- Data licence Germany zero version 2.0
- David M. Gay dtoa License
- DEC 3-Clause License
- Detection Rule License 1.0
- Detection Rule License 1.1
- Deutsche Freie Software Lizenz
- diffmark license
- DOC License
- DocBook Schema License
- DocBook Stylesheet License
- DocBook XML License
- Dotseqn License
- DSDP License
- dvipdfm License
- Eclipse public license 1.0 (epl-1.0)
- Eclipse public license 2.0 (epl-2.0)
- eCos license version 2.0
- Educational Community License v1.0
- Educational Community License v2.0
- eGenix.com Public License 1.1.0
- Eiffel Forum License v1.0
- Eiffel Forum License v2.0
- Elastic License 2.0
- Enlightenment License (e16)
- enna License
- Entessa Public License v1.0
- EPICS Open License
- Erlang Public License v1.1
- Etalab Open License 2.0
- EU DataGrid Software License
- European Union Public License 1.0
- European Union Public License 1.1
- European Union Public License 1.2
- Eurosym License
- Fair License
- feh License
- Ferguson Twofish License
- Frameworx Open License 1.0
- Fraunhofer FDK AAC Codec Library
- FreeBSD Documentation License
- FreeImage Public License v1.0
- Freetype Project License
- FSF All Permissive License
- FSF All Permissive License (without Warranty)
- FSF Unlimited License
- FSF Unlimited License (with License Retention)
- FSF Unlimited License (With License Retention and Warranty Disclaimer)
- Furuseth License
- Fuzzy Bitmap License
- fwlw License
- GD License
- Generic XTS License
- Giftware License
- GL2PS License
- Glulxe License
- Gnome GCR Documentation License
- GNU Affero general public license (apl)
- GNU Affero General Public License v1.0 only
- GNU Affero General Public License v1.0 or later
- GNU Affero General Public License v2.0 only
- GNU Affero General Public License v2.0 or later
- GNU Affero General Public License v3.0 only
- GNU Affero General Public License v3.0 or later
- GNU Free Documentation License v1.1 only
- GNU Free Documentation License v1.1 only - invariants
- GNU Free Documentation License v1.1 only - no invariants
- GNU Free Documentation License v1.1 or later
- GNU Free Documentation License v1.1 or later - invariants
- GNU Free Documentation License v1.1 or later - no invariants
- GNU Free Documentation License v1.2 only
- GNU Free Documentation License v1.2 only - invariants
- GNU Free Documentation License v1.2 only - no invariants
- GNU Free Documentation License v1.2 or later
- GNU Free Documentation License v1.2 or later - invariants
- GNU Free Documentation License v1.2 or later - no invariants
- GNU Free Documentation License v1.3 only
- GNU Free Documentation License v1.3 only - invariants
- GNU Free Documentation License v1.3 only - no invariants
- GNU Free Documentation License v1.3 or later
- GNU Free Documentation License v1.3 or later - invariants
- GNU Free Documentation License v1.3 or later - no invariants
- GNU General Public License v1.0 only
- GNU General Public License v1.0 or later
- GNU General Public License v2.0 only
- GNU General Public License v2.0 or later
- GNU General Public License v2.0 w/autoconf exception
- GNU General Public License v2.0 w/bison exception
- GNU General Public License v2.0 w/classpath exception
- GNU General Public License v2.0 w/font exception
- GNU General Public License v2.0 w/gcc runtime library exception
- GNU General Public License v3.0 only
- GNU General Public License v3.0 or later
- GNU General Public License v3.0 w/autoconf exception
- GNU General Public License v3.0 w/gcc runtime library exception
- GNU Lesser General Public License v2.0 only
- GNU Lesser General Public License v2.1 only
- GNU Lesser General Public License v2.1 or later
- GNU Lesser General Public License v3.0 only
- GNU Lesser General Public License v3.0 or later
- GNU lesser general public license
- GNU Library General Public License v1 only
- GNU Library General Public License v1 or later
- GNU Library General Public License v2 only
- GNU Library General Public License v2 or later
- GNU general public license
- GNU general public license v2 (gplv2)
- gnuplot License
- Good Luck With That Public License
- Graphics Gems License
- gSOAP Public License v1.3b
- gtkbook License
- Gutmann License
- Haskell Language Report License
- hdparm License
- Hewlett-Packard 1986 License
- Hewlett-Packard 1989 License
- Hewlett-Packard BSD variant license
- HIDAPI License
- Hippocratic License 2.1
- Historical Permission Notice and Disclaimer (HPND)
- Historical Permission Notice and Disclaimer - DEC variant
- Historical Permission Notice and Disclaimer - documentation sell variant
- Historical Permission Notice and Disclaimer - documentation variant
- Historical Permission Notice and Disclaimer - Fenneberg-Livingston variant
- Historical Permission Notice and Disclaimer - INRIA-IMAG variant
- Historical Permission Notice and Disclaimer - Intel variant
- Historical Permission Notice and Disclaimer - Kevlin Henney variant
- Historical Permission Notice and Disclaimer - Markus Kuhn variant
- Historical Permission Notice and Disclaimer - merchantability variant
- Historical Permission Notice and Disclaimer - Netrek variant
- Historical Permission Notice and Disclaimer - Pbmplus variant
- Historical Permission Notice and Disclaimer - sell regexpr variant
- Historical Permission Notice and Disclaimer - sell variant
- Historical Permission Notice and Disclaimer - sell xserver variant with MIT disclaimer
- Historical Permission Notice and Disclaimer - University of California, US export warning
- Historical Permission Notice and Disclaimer - University of California variant
- Historical Permission Notice and Disclaimer with MIT disclaimer
- HPND sell variant with MIT disclaimer
- HPND sell variant with MIT disclaimer - reverse
- HPND with US Government export control and 2 disclaimers
- HPND with US Government export control warning
- HPND with US Government export control warning and acknowledgment
- HPND with US Government export control warning and modification rqmt
- HTML Tidy License
- IBM PowerPC Initialization and Boot Software
- IBM Public License v1.0
- ICU License
- IEC Code Components End-user licence agreement
- ImageMagick License
- iMatix Standard Function Library Agreement
- Imlib2 License
- Independent JPEG Group License
- Independent JPEG Group License - short
- Info-ZIP License
- Inner Net License v2.0
- Inno Setup License
- Intel ACPI Software License Agreement
- Intel Open Source License
- Interbase Public License v1.0
- IPA Font License
- ISC License
- ISC Veillard variant
- ISC license (iscl)
- Jam License
- Japan Network Information Center License
- JasPer License
- JPL Image Use Policy
- JSON License
- Kastrup License
- Kazlib License
- Knuth CTAN License
- LaTeX Project Public License v1.0
- LaTeX Project Public License v1.1
- LaTeX Project Public License v1.2
- LaTeX Project Public License v1.3a
- LaTeX Project Public License v1.3c
- Latex2e License
- Latex2e with translated notice permission
- Lawrence Berkeley National Labs BSD variant license
- Leptonica License
- Lesser General Public License For Linguistic Resources
- libpng License
- libselinux public domain notice
- libtiff License
- libutil David Nugent License
- Licence Art Libre 1.2
- Licence Art Libre 1.3
- Licence Libre du Québec Permissive version 1.1
- Licence Libre du Québec Réciprocité forte version 1.1
- Licence Libre du Québec Réciprocité version 1.1
- Linux Kernel Variant of OpenIB.org license
- Linux man-pages - 1 paragraph
- Linux man-pages Copyleft
- Linux man-pages Copyleft - 2 paragraphs
- Linux man-pages Copyleft Variant
- LPD Documentation License
- lsof License
- Lucent Public License v1.02
- Lucent Public License Version 1.0
- Lucida Bitmap Fonts License
- LZMA SDK License (versions 9.11 to 9.20)
- LZMA SDK License (versions 9.22 and beyond)
- Mackerras 3-Clause - acknowledgment variant
- Mackerras 3-Clause License
- magaz License
- mailprio License
- MakeIndex License
- Martin Birgmeier License
- Matrix Template Library License
- McPhee Slideshow License
- metamail License
- Michigan/Merit Networks License
- Microsoft Limited Public License
- Microsoft Public License
- Microsoft Reciprocal License
- Minpack License
- MIPS License
- MIT Click License
- CMU License (MIT-CMU)
- MIT Festival Variant
- MIT Khronos - old variant
- MIT license
- MIT License Modern Variant
- MIT +no-false-attribs license
- MIT Open Group variant
- MIT testregex Variant
- MIT Tom Wu Variant
- MIT No Attribution
- MMIXware License
- Motosoto License
- Mozilla Public License 1.0
- Mozilla Public License 1.1
- Mozilla Public License 2.0 (no copyleft exception)
- Mozilla public license (mpl)
- Mozilla public license 2.0 (mpl 2.0)
- MPEG Software Simulation
- mpi Permissive License
- mpich2 License
- mplus Font License
- Mulan Permissive Software License, Version 1
- Mulan Permissive Software License, Version 2
- Multics License
- Mup License
- Nara Institute of Science and Technology License (2003)
- NASA Open Source Agreement 1.3
- Naumen Public License
- NCBI Public Domain Notice
- NCL Source Code License
- Net Boolean Public License v1
- Net-SNMP License
- NetCDF license
- Nethack General Public License
- Netizen Open Source License
- Netscape Public License v1.0
- Netscape Public License v1.1
- Newsletr License
- NICTA Public Software License, Version 1.0
- NIST Public Domain Notice
- NIST Public Domain Notice with license fallback
- NIST Software License
- No Limit Public License
- Nokia Open Source License
- Non-Commercial Government Licence
- Non-Profit Open Software License 3.0
- Norwegian Licence for Open Government Data (NLOD) 1.0
- Norwegian Licence for Open Government Data (NLOD) 2.0
- Noweb License
- NRL License
- NTP License
- NTP No Attribution
- Nunit License
- OAR License
- OCLC Research Public License 2.0
- OFFIS License
- OGC Software License, Version 1.0
- Open CASCADE Technology Public License
- Open Data Commons Attribution License v1.0
- Open Data Commons Open Database License v1.0
- Open Data Commons Public Domain Dedication & License 1.0
- Open Government Licence - Canada
- Open Government Licence v1.0
- Open Government Licence v2.0
- Open Government Licence v3.0
- Open Group Test Suite License
- Open LDAP Public License 2.2.2
- Open LDAP Public License v1.1
- Open LDAP Public License v1.2
- Open LDAP Public License v1.3
- Open LDAP Public License v1.4
- Open LDAP Public License v2.0.1
- Open LDAP Public License v2.0 (or possibly 2.0A and 2.0B)
- Open LDAP Public License v2.1
- Open LDAP Public License v2.2
- Open LDAP Public License v2.2.1
- Open LDAP Public License v2.3
- Open LDAP Public License v2.4
- Open LDAP Public License v2.5
- Open LDAP Public License v2.6
- Open LDAP Public License v2.7
- Open LDAP Public License v2.8
- Open Logistics Foundation License Version 1.3
- Open Market License
- Open Public License v1.0
- Open Publication License v1.0
- Open Software License 1.0
- Open Software License 1.1
- Open Software License 2.0
- Open Software License 2.1
- Open Software License 3.0
- Open Use of Data Agreement v1.0
- OpenPBS v2.3 Software License
- OpenSSL License
- OpenSSL License - standalone
- OpenVision License
- OSET Public License version 2.1
- PADL License
- Peer Production License
- PHP License v3.0
- PHP License v3.01
- Pixar License
- pkgconf License
- Plexus Classworlds License
- PNG Reference Library version 2
- pnmstitch License
- PolyForm Noncommercial License 1.0.0
- PolyForm Small Business License 1.0.0
- PostgreSQL License
- psfrag License
- psutils License
- Public domain
- Python ldap License
- Python software foundation license
- Python License 2.0
- Python License 2.0.1
- Python software foundation license v1
- Python software foundation license v2
- Python Software Foundation License 2.0
- Q Public License 1.0
- Q Public License 1.0 - INRIA 2004 variant
- Qhull License
- radvd License
- Rdisc License
- RealNetworks Public Source License v1.0
- Reciprocal Public License 1.1
- Reciprocal Public License 1.5
- Red Hat eCos Public License v1.1
- Repoze public license
- Ricoh Source Code Public License
- RSA Message-Digest License
- Ruby License
- Ruby pty extension license
- Sax Public Domain Notice
- Sax Public Domain Notice 2.0
- Saxpath License
- SCEA Shared Source License
- Scheme Language Report License
- Scheme Widget Library (SWL) Software License Agreement
- Secure Messaging Protocol Public License
- Sendmail License
- Sendmail License 8.23
- Sendmail Open Source License v1.1
- Server Side Public License, v 1
- SGI Free Software License B v1.0
- SGI Free Software License B v1.1
- SGI Free Software License B v2.0
- SGI OpenGL License
- SGP4 Permission Notice
- SIL Open Font License 1.0
- SIL Open Font License 1.0 with no Reserved Font Name
- SIL Open Font License 1.0 with Reserved Font Name
- SIL Open Font License 1.1
- SIL Open Font License 1.1 with no Reserved Font Name
- SIL Open Font License 1.1 with Reserved Font Name
- Simple Public License 2.0
- SL License
- Sleepycat License
- SMAIL General Public License
- SNIA Public License 1.1
- snprintf License
- softSurfer License
- Solderpad Hardware License, Version 0.51
- Solderpad Hardware License v0.5
- Soundex License
- 3D Slicer License v1.0
- 3dfx Glide License
- Spencer License 86
- Spencer License 94
- Spencer License 99
- SQLite Blessing
- ssh-keyscan License
- SSH OpenSSH license
- SSH short notice
- SSLeay License - standalone
- Standard ML of New Jersey License
- SugarCRM Public License v1.1.3
- Sun Industry Standards Source License v1.1
- Sun Industry Standards Source License v1.2
- Sun PPP License
- Sun PPP License (2000)
- Sun Public License v1.0
- SunPro License
- swrule License
- Sybase Open Watcom Public License 1.0
- Symlinks License
- Systemics BSD variant license
- Systemics W3Works BSD variant license
- Taiwan Open Government Data License, version 1.0
- TAPR Open Hardware License v1.0
- TCL/TK License
- TCP Wrappers License
- Technische Universitaet Berlin License 1.0
- Technische Universitaet Berlin License 2.0
- TermReadKey License
- Text-Tabs+Wrap License
- The MirOS Licence
- The Parity Public License 6.0.0
- The Parity Public License 7.0.0
- ThirdEye License
- THOR Public License 1.0
- threeparttable License
- Time::ParseDate License
- TMate Open Source License
- TORQUE v2.5+ Software License v1.1
- Transitive Grace Period Public Licence 1.0
- Trusster Open Source License
- TrustedQSL License
- TTYP0 License
- Ubuntu Font Licence v1.0
- UCAR License
- ulem License
- Unicode License Agreement - Data Files and Software (2015)
- Unicode License Agreement - Data Files and Software (2016)
- Unicode License v3
- Unicode Terms of Use
- United Kingdom Open Parliament Licence v3.0
- Universal Permissive License v1.0
- University of Illinois/NCSA Open Source License
- UnixCrypt License
- The Unlicense (Unlicense)
- Upstream Compatibility License v1.0
- Utah Raster Toolkit Run Length Encoded License
- Vim License
- VOSTROM Public License for Open Source
- Vovida Software License v1.0
- W3C Software Notice and Document License (2015-05-13)
- W3C Software Notice and License (1998-07-20)
- W3C Software Notice and License (2002-12-31)
- w3m License
- Widget Workshop License
- Wsuipa License
- DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
- WWL License
- wxWindows Library License
- X.Net License
- X11 License
- X11 License Distribution Modification Variant
- X11 swapped final paragraphs
- Xdebug License v 1.03
- Xerox License
- Xfig License
- XFree86 License 1.1
- xinetd License
- xkeyboard-config Zinoviev License
- xlock License
- XPP License
- XSkat License
- xzoom License
- Yahoo! Public License v1.0
- Yahoo! Public License v1.1
- Zed License
- Zeeff License
- Zend License v2.0
- Zimbra Public License v1.3
- Zimbra Public License v1.4
- zlib/libpng License with Acknowledgement
- zlib License
- Zope Public License
- Zope Public License 1.1
- Zope Public License 2.0
- Zope Public License 2.1
- Zope Public License v1
- Zope Public License v2

## Credits

- Tom Nijhof
