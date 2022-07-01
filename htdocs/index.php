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
$query = $con->query("
(SELECT * FROM fishbowl.fish_activity ORDER BY Date DESC limit 30) ORDER BY Time ASC
");

foreach($query as $data)
{
$date[] = $data['Date'];
$time[] = $data['Time'];
$num[] = $data['num_obj'];
$mobility[] = $data['mobility'];
}

$frontString = "현재 인식된 물고기 개체 수 : ".'<font color="red"><font size=6>'.'2'.'</font></font>'." 마리";
?>
<?php echo '<center><font size=5>'.$frontString; ?>
<div>
<canvas id="myChart"; style="width: 500px;height: 700px"></canvas>
</div>

<script>
// === include 'setup' then 'config' above ===
const labels = <?php echo json_encode($time) ?>;
const data = {
labels: labels,
datasets: [{
label: 'Fish01',
data: <?php echo json_encode($num) ?>,
backgroundColor:
'rgba(0, 0, 255, 0.4)',
borderColor: 
'rgb(0, 0, 255)'
,
borderWidth: 1,
pointStyle: 'circle',
pointRadius: 5,
pointHoverRadius: 15
}, {
label: 'Fish02',
data: <?php echo json_encode($mobility) ?>,
backgroundColor:
'rgba(255, 0, 0, 0.4)',
borderColor: 
'rgb(255, 0, 0)'
,
borderWidth: 1,
pointStyle: 'circle',
pointRadius: 5,
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
max:15,
stepsize:1,
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