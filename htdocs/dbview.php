<!DOCTYPE html>
<html>
<body style="background-color:#48b3bc">
<?php
ob_start();
$servername = "localhost";
$username = "root";
$password = "as19778797";
$dbname = "fishbowl";
 
$conn = mysqli_connect($servername, $username, $password, $dbname);

$sql = "select * from sensing_data order by Date desc";

echo "<style>td { border:1px solid #ccc; padding:5px; }</style>";
echo "<table><tbody>";

$result = mysqli_query($conn, $sql);
   if (mysqli_num_rows($result) > 0) {
   while($row = mysqli_fetch_assoc($result)) {
   echo"<tr>";
   echo "<font size=6 color=white>" . "날짜: @" . $row["Date"]. " / 시간: @" . $row["Time"]. " / 수온: @" . $row["water_temp"]. "<br>";
   echo "<br>";
   echo"</tr>";
   }
   }else{
   echo "테이블에 데이터가 없습니다.";
   }

   echo"</tbody></table>";

header("Refresh:60");

mysqli_query($conn, $sql);
mysqli_close($conn);
?>

</body>
</html>