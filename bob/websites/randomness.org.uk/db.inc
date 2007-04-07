<?
$PHP_SELF=$_SERVER["PHP_SELF"];
$database=bob;
mysql_pconnect ("localhost","bob","greeble");
$visitor=mysql_db_query($database,"select * from impbob2 where page='$PHP_SELF'");
$time=date("U");
$result=mysql_db_query($database,"insert into impbob2 values
('','$time','$REMOTE_ADDR','$PHP_SELF')");
$up=mysql_db_query($database,"select * from linker where pagename='$PHP_SELF' and parent!=''");
$across=mysql_db_query($database,"select * from linker where pagename='$PHP_SELF' and parent!=''");
$uprow=mysql_num_rows($up);
$down=mysql_db_query($database,"select * from linker where parent='$PHP_SELF'");
$downrow=mysql_num_rows($down);
?>

