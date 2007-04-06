plan(9);

var tp = new TagEngine();
assert(tp instanceof TagEngine);

var aTagString = "news booty bbc";
assert(tp.parse(aTagString));

var tags = tp.parse(aTagString);
assert( tags instanceof Array );
assertEquals( tags.length, 3 );

aTagString = '"james duncan" news booty bbc';
tags = tp.parse(aTagString);
assertEquals( tags.length, 4 );

tp.tag( "http://www.fotango.com", "zimki javascript foo");
var theTag = Tag.tagFor('zimki');
assert(theTag.hasTagged('http://www.fotango.com'));

var theUrl = URL.urlFor('http://www.fotango.com');
assert(theUrl.hasTag('zimki'));
assertEquals(theUrl.tags, "zimki javascript foo");

tp.tag("http://www.zimki.com", '"server-side javascript" javascript foo');
theUrl = URL.urlFor("http://www.zimki.com");
assertEquals(theUrl.tags, '"server-side javascript" javascript foo');

