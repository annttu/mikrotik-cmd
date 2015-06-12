Mikrotik-API
===

Python interface and command line tool for Mikrotik API.

Usage
=====

Usage tries to be similar to cli. Commands are prefixed with same paths as in ssh. Options are given using key=value syntax.

print
-----

    /path print [where arg1=value1 [arg2=value2] ...]

Print prints current status of values in given path. Optional where limits query output to contain only values with those values set.
    
set
---

    /path set [id] arg1=value1 [arg2=value2] ...

Set sets new values for existing rows. Id is mandatory if value have ``.id`` attribute. 

add
---

    /path add arg1=value1 [arg2=value2] ...
    
Add adds new row to path.

remove
----

     /path remove id

Remove removes row from path with id ``id``

License
========

The MIT License (MIT)

Copyright (c) 2015 Antti Jaakkola

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
