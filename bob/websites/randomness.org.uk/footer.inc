<? 
if ($uprow!="0"){
echo "UP:";
};
?>
<? while ($uplink=mysql_fetch_row($up)){
$upresult=mysql_db_query($database,"select * from linker where pagename='$uplink[3]'");
$uptitle=mysql_fetch_row($upresult);
if ($uptitle[1]!=""){
echo "<a href=$uplink[3]>$uptitle[1]</a>:";
};
};?>
<br>
<?
if ($uprow!="0"){
echo "ACROSS:";
};
?>
<? while ($accrosslink=mysql_fetch_row($across)){
#echo "$accrosslink";
$acrossresult=mysql_db_query($database,"select * from linker where parent='$accrosslink[3]' and pagename!='$PHP_SELF'");
#echo $acrossresult;
#echo "first across loop";
while ($acrosstitle=mysql_fetch_row($acrossresult)){
echo "<a href=$acrosstitle[2]>$acrosstitle[1]</a>:";
};
};?>



<br>
<?
if ($downrow!="0"){
echo "DOWN:";
};
?>
<? while ($downlink=mysql_fetch_row($down)){
echo "<a href=$downlink[2]>$downlink[1]</a>:";
};?>
<hr>
<div align=center>
Contact the <a href="mailto:webmaster@randomness.org.uk?<?echo $PHP_SELF;?>">webmaster</a> if you have a query.<br>
<!-- Last Updated -->
<? # echo date( " dmY H:i", filemtime(index.php) );
 ?>
<br>
Number of hits:
<? 
echo mysql_num_rows($visitor);?>
</div>
