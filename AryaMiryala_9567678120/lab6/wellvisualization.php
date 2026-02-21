<?php
header('Content-Type: application/json; charset=utf-8');

// DB credentials - change before commit or else pass and stuff will be out in publicc
$host = '127.0.0.1';
$db   = 'dsci560_wells';
$user = 'root';     // change
$pass = ''; // change or leave empty if using socket auth

$opts = [
    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
];

$dsn = "mysql:host=$host;dbname=$db;charset=utf8mb4";
$pdo = new PDO($dsn, $user, $pass, $opts);

// fetch wells and stim rows
$sql = "
SELECT w.api, w.well_name, w.latitude, w.longitude, w.status, w.well_type,
       w.closest_city, w.barrels_oil, w.barrels_gas, w.raw_text, w.notes,
       s.id as stim_id, s.stage, s.fluid_vol, s.proppant_lbs, s.chemicals, s.other_fields
FROM wells w
LEFT JOIN stimulation s ON s.well_api = w.api
ORDER BY w.api, s.stage
";

$stmt = $pdo->query($sql);
$rows = $stmt->fetchAll();

$features = [];
$index = []; // api -> feature index

foreach ($rows as $r) {
    $api = $r['api'];
    if (!isset($index[$api])) {
        $props = [
            'api' => $api,
            'well_name' => $r['well_name'],
            'status' => $r['status'],
            'well_type' => $r['well_type'],
            'closest_city' => $r['closest_city'],
            'barrels_oil' => is_null($r['barrels_oil']) ? null : (float)$r['barrels_oil'],
            'barrels_gas' => is_null($r['barrels_gas']) ? null : (float)$r['barrels_gas'],
            'raw_text' => $r['raw_text'] ? json_decode($r['raw_text'], true) : null,
            'notes' => $r['notes'],
            'stimulation' => []
        ];

        $lon = is_null($r['longitude']) ? null : (float)$r['longitude'];
        $lat = is_null($r['latitude']) ? null : (float)$r['latitude'];

        $feat = [
            'type' => 'Feature',
            'properties' => $props,
            'geometry' => [
                'type' => 'Point',
                'coordinates' => [$lon, $lat]
            ]
        ];
        $index[$api] = count($features);
        $features[] = $feat;
    }

    if (!is_null($r['stim_id'])) {
        $idx = $index[$api];
        $features[$idx]['properties']['stimulation'][] = [
            'id' => (int)$r['stim_id'],
            'stage' => is_null($r['stage']) ? null : (int)$r['stage'],
            'fluid_vol' => is_null($r['fluid_vol']) ? null : (float)$r['fluid_vol'],
            'proppant_lbs' => is_null($r['proppant_lbs']) ? null : (float)$r['proppant_lbs'],
            'chemicals' => $r['chemicals'],
            'other_fields' => $r['other_fields'] ? json_decode($r['other_fields'], true) : null
        ];
    }
}

$fc = ['type' => 'FeatureCollection', 'features' => $features];
echo json_encode($fc, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT);