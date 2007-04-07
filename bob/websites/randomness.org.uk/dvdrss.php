<? include "db.inc" ?>
<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN" "http://my.n
etscape.com/publish/formats/rss-0.91.dtd">

<rss version="0.91">
<channel>
<title>random dvd for bob</title>
  <link></link>
  <description></description>
  <item>
      <title>
<?
$dvdresult=mysql_db_query(dvd,"select title from dvd where owner='bob' order by RAND() limit 1");
$rsstitle=mysql_fetch_row($dvdresult);
echo $rsstitle[0];
?>
</title>
      <link></link>
  </item>
</channel>
</rss>

