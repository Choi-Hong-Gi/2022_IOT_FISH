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
(SELECT * FROM sensing_data ORDER BY Date DESC limit 10) ORDER BY Time ASC;
");

foreach($query as $data)
{
$date[] = $data['Date'];
$time[] = $data['Time'];
$temp[] = $data['water_temp'];
}

?>

<div>
<canvas id="myChart"; style="width: 400px;height: 600px"></canvas>
</div>

<script>
// === include 'setup' then 'config' above ===
const labels = <?php echo json_encode($time) ?>;
const data = {
labels: labels,
datasets: [{
label: '수온',
data: <?php echo json_encode($temp) ?>,
backgroundColor: [
'rgba(255, 99, 132, 0.2)',
'rgba(255, 159, 64, 0.2)',
'rgba(255, 205, 86, 0.2)',
'rgba(75, 192, 192, 0.2)',
'rgba(54, 162, 235, 0.2)',
'rgba(153, 102, 255, 0.2)',
'rgba(201, 203, 207, 0.2)'
],
borderColor: [
'rgb(255, 99, 132)',
'rgb(255, 159, 64)',
'rgb(255, 205, 86)',
'rgb(75, 192, 192)',
'rgb(54, 162, 235)',
'rgb(153, 102, 255)',
'rgb(201, 203, 207)'
],
borderWidth: 1,
pointStyle: 'circle',
pointRadius: 10,
pointHoverRadius: 15
}]
};

const config = {
type: 'line',
data: data,
responsive: true,
options: {
  scales: {
    xAxes: [{
               ticks:{
                  fontColor : 'rgba(12, 13, 13, 1)',
                  fontSize : 25,
               },
               gridLines:{
                  color: "rgba(87, 152, 23, 1)",
                  lineWidth: 3
               }
            }],

y: {
beginAtZero: true,
max:40,
min:10,
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

