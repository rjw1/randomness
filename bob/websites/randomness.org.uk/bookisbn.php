<? include "db.inc";?>
<html>
<head>
	<title>Book List</title>
<link rel=stylesheet type="text/css" href="randomness.css" title="style">
</head>
<? include "body.inc";?> 


<h1 class=title1 >randomness.org.uk</h1><p>
<h2 class=title2 >book Listing</h2><p>
<div class=ident align=left>
<? 
$bookresult=mysql_db_query(bob_books,"select books.book_title,books.book_author,books.book_isbn  from books  order by books.book_title");
?>
<TABLE align=center BORDER="0" WIDTH="97%">
  <TR>
   <td><b>Title</b></td>
        <td><b>Author</b></td>
	<td><b>isbn</b></td>
      </TR>
<?
while ($text=mysql_fetch_row($bookresult)){
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

