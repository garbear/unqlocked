== UnQlocked by Garrett a.k.a. garbear ==

UnQlocked is a script to display the current time using common phrases instead
of numbers. Originally an unabashed ripoff of Biegert & Funk's awesome product,
this script has been extended to support a much larger set of languages and
configurations.

An up-to-date copy of the code can be found at the project's GitHub page:
https://github.com/garbear/unqlocked

Limited support is available on the XBMC forum. You may also find additional
clocks and themes:
http://forum.xbmc.org/showthread.php?tid=135578


== How to run ==
XBMC Frodo will feature Python screensaver support. When you upgrade your XBMC
install to a compatable version, script.unqlocked will show up in your list of
screensavers. Until then, this script can also be run from the Programs menu
like any other add-on.


== Creating your own clock ==
Clocks are defined by an XML layout file in the layouts folder. In the root
<layout> tag you will need three tags.
* <background>
    A comma-separated list of entities. Each entity can be multiple
    characters (such as L' or AE). Whitespace is ignore, so use multiple lines
    for clarity. The number of entities must be equal to width * height (given
    by the width and height attributes of the <background> tag).
* <strings>
    A mapping of numbers to strings. If your clock uses a number, make sure the
    strings table has an entry for it.
* <times>
    Time strings can use symbols to represent the strings found in the strings
    table. UnQlocked will identify the offset and direction of the symbol and
    propagate it forward in time, making it possible to define a large
    expression of times using a single string.

Not everything can be accomplished with symbols, however. If your <time> string
includes no symbols, it won't be propagated forward and will only occur for
that instant. To extend such a string, you can use a "duration" attribute in
the same format as the "id" attribute. For example:
    <time id="2:00">%2h% o'clock</time>
    <time id="2:30" duration="0:10">lunch time</time>
Here, 2:25 and 2:40 would read "two o'clock", and 2:30 and 2:35 would read
"lunch time". Remember that your layout needs all these strings embedded in the
background. Also, note that the duration attribute can be used in times with
symbols as well (if the need arises).

If the "use24" attribute is set to true, UnQlocked will use a 24-hour system.

UnQlocked uses GCD to determine your clock's resolution. Seconds symbols can be
used, but no special handling is done for them, so you may need to perform lots
of copy-pasting for anything outside the "X hours Y minutes Z seconds" format.


== Creating your own theme ==
A theme is an XML file with the following tags:
* <background>
    This color (AARRGGBB) is applied fullscreen. If the AA channel is less than
    FF, the background will be slightly transparent. This means that when being
    run as a script, the skin will still be visible; when being run as a
    screensaver, the underlying window is black, so the background will just
    appear darker than it should. Skin color names can also be used here (but
    the skin must support it, so try to stick with common names).
* <image>
    An optional image behind the clock. Attributes "width" and "height" can be
    specified (the image is always centered). If width and height are set to
    1280 and 720 (or omitted), the image will be fullscreen, making the
    <background> tag optional.
* <active>
* <inactive>
    The text color and active (highlighted) and inactive letters.
