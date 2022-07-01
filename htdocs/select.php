<!DOCTYPE html>
<html>
<body bgcolor='#2f88b2'>

<?php
$servername = "localhost";
$username = "root";
$password = "as19778797";
$dbname = "fishbowl";

// 접속 생성
$conn = new mysqli($servername, $username, $password, $dbname);
// 접속 체크
if ($conn->connect_error) {
  die("접속 실패: " . $conn->connect_error);
}

$sql = "SELECT * FROM sensing_data order by Date desc limit 1";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
 while($row = $result -> fetch_assoc()){
  echo "<font size=5 color=white>". $row["water_temp"]."<br>";

 }
} else {
  echo "데이터가 없습니다.";
}
header("Refresh:60");
$conn->close();
?>

</body>
</html>