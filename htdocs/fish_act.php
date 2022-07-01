<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<title>Document</title>
</head>
<body>

<?php
$con = new mysqli('localhost','root','as19778797','fishbowl');
$query01 = $con->query("
(SELECT * FROM mobility where obj_id = 'fish01' ORDER BY Date DESC limit 10) ORDER BY Time ASC
");

$query02 = $con->query("
(SELECT * FROM mobility where obj_id = 'fish02' ORDER BY Date DESC limit 10) ORDER BY Time ASC
");

foreach($query01 as $data)
{
$date[] = $data['Date'];
$time[] = $data['Time'];
$label01[] = $data['obj_id'];
$num[] = $data['obj_num'];
$mobility01[] = $data['mobility'];
}

foreach($query02 as $data)
{
$label02[] = $data['obj_id'];
$mobility02[] = $data['mobility'];
}

$frontString = "현재 인식된 물고기 개체 수 : ".'<font color="green"><font size=5>'.max($num).'</font></font>'." 마리";
?>
<?php echo '<center><font size=4>'.$frontString; ?>
<div>
<canvas id="myChart"; style="width: 500px;height: 700px"></canvas>
</div>

<script>
// === include 'setup' then 'config' above ===
const labels = <?php echo json_encode($time) ?>;
const data = {
labels: labels,
datasets: [{
label: 'fish01',
data: <?php echo json_encode($mobility01) ?>,
backgroundColor:
'rgba(200, 200, 0, 0.4)',
borderColor: 
'rgb(200, 200, 0)'
,
borderWidth: 1,
pointStyle: 'circle',
pointRadius: 10,
pointHoverRadius: 15
},
{
label: 'fish02',
data: <?php echo json_encode($mobility02) ?>,
backgroundColor:
'rgba(0, 0, 0, 0.4)',
borderColor: 
'rgb(0, 0, 0)'
,
borderWidth: 1,
pointStyle: 'circle',
pointRadius: 10,
pointHoverRadius: 15
}]
};

const config = {
type: 'line',
data: data,
responsive: false,
options: {

scales: {
y: {
beginAtZero: false,
max:50
}
}
},
plugins: {
title: {
display: true,
text: (ctx) => 'Point Style: ' + ctx.chart.data.datasets[0].pointStyle,
}
}
};
Chart.defaults.font.size = 20;
var myChart = new Chart(
document.getElementById('myChart'),
config
);

</script>

</body>
</html>