<? include "db.inc";?>
<html>
<head>
	<title>Dvd Stuff</title>
<link rel=stylesheet type="text/css" href="randomness.css" title="style">
</head>
<? include "body.inc";?> 


<h1 class=title1 >randomness.org.uk</h1><p>
<h2 class=title2 >DVD Listing</h2><p>
<div class=ident align=left>
<? 
$dvdresult=mysql_db_query(dvd,"select dvd.title,owner.name,dvd.region  from dvd,owner where dvd.owner=owner.name order by dvd.title");
?>
<TABLE align=center BORDER="0" WIDTH="97%">
  <TR>
   <td><b>Title</b></td>
        <td><b>Owner</b></td>
        <td><b>Region</b></td>
      </TR>
<?
while ($text=mysql_fetch_row($dvdresult)){
echo "<td>$text[0]</td>";
echo "<td>$text[1]</td>";
echo "<td>$text[2]</td></tr>";

};
echo "</TABLE>";

?>
</div>
<? include "footer.inc";?>
</body>
</html>

