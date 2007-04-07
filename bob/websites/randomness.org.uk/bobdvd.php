<? include "db.inc";?>
<html>
<head>
	<title>Dvd Stuff</title>
<link rel=stylesheet type="text/css" href="randomness.css" title="style">
</head>
<? include "body.inc";?> 


<h2 class=title2 >DVDs</h2><p>
<div class=ident align=left>
<? 
$dvdresult=mysql_db_query(dvd,"select * from dvd where owner='bob' order by title");
?>
<?
while ($text=mysql_fetch_row($dvdresult)){
echo "$text[1]<br /><br />";

};

?>
</div>
</body>
</html>

