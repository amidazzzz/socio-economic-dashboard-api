# Frontend API Guide

## 1. Base

- API prefix: `/api`
- Health: `GET /health`
- Swagger: `GET /docs`
- OpenAPI: `GET /openapi.json`
- Auth: not required

Local example:

```text
http://localhost:8000
```

---

## 2. Backend scope

The backend currently exposes analytics for three blocks:

1. Demography
   `population`, `natural_increase`, `migration_balance`
2. Labour and income
   `unemployment_rate`, `average_salary`
3. Economy
   `vrp`, `vrp_per_capita`

Important metric note:

- `average_salary` is currently loaded from `AVERAGE_SALARY_REAL_INDEX`
- this is a real wage index, not nominal salary in rubles
- frontend should label it accordingly unless backend later receives absolute salary values

---

## 3. Recommended frontend bootstrap

1. Request `GET /api/regions`
2. Request `GET /api/indicators`
3. Build `indicatorCode -> indicatorId` map
4. Use:
   - `/api/values` for raw indicator series
   - `/api/analytics/*` for derived metrics, rankings, normalization and composite scores

Never hardcode `indicator_id`.

---

## 4. Dictionary endpoints

### `GET /api/regions`

Response item:

```json
{
  "id": 63,
  "code": "63000000000",
  "name": "Самарская область",
  "type": "oblast",
  "parent_id": null
}
```

### `GET /api/indicators`

Response item:

```json
{
  "id": 3,
  "code": "UNEMPLOYMENT_RATE",
  "name": "Уровень безработицы",
  "description": "Уровень безработицы по методологии МОТ",
  "unit": {
    "id": 2,
    "code": "PERCENT",
    "name": "процент"
  }
}
```

Current indicator codes:

- `POPULATION_TOTAL`
- `UNEMPLOYMENT_RATE`
- `NATURAL_INCREASE`
- `MIGRATION_BALANCE_RATE`
- `AVERAGE_SALARY_REAL_INDEX`
- `VRP_TOTAL`

### `GET /api/values`

Query params:

- `indicator_id` required
- `region_id` required
- `start_year` optional
- `end_year` optional
- `period` optional, default `year`

Response:

```json
{
  "indicator_id": 3,
  "region_id": 63,
  "series": [
    { "year": 2019, "value": 3.9 },
    { "year": 2020, "value": 4.9 }
  ]
}
```

Use `/api/values` for raw charts of any single indicator.

---

## 5. Analytics dataset

### `GET /api/analytics/dataset`

Query params:

- `region_id` optional
- `start_year` optional
- `end_year` optional

This is the main cross-indicator dataset for dashboards and tables.

Response item:

```json
{
  "region_id": 63,
  "region_name": "Самарская область",
  "year": 2023,
  "population": 3156432.0,
  "unemployment_rate": 3.6,
  "natural_increase": -10219.0,
  "migration_balance": 18.3,
  "average_salary": 116.1,
  "vrp": 693379400.0
}
```

Notes:

- fields may be `null` if a source does not have this year
- year range is no longer restricted to the previous narrow window
- effective range depends on actual source files for each indicator

### `GET /api/analytics/region/{region_id}`

Same structure as dataset, but only for one region and sorted by year.

---

## 6. Region derived metrics

### `GET /api/analytics/region/{region_id}/metrics`
Alias: `GET /api/analytics/region/{region_id}/growth`

Derived series by year:

```json
{
  "year": 2023,
  "population_growth_rate": -0.0021,
  "salary_growth_rate": 0.041,
  "vrp_growth_rate": 0.065,
  "unemployment_delta": -0.1,
  "natural_increase_delta": 604.0,
  "adjusted_population_change": -0.0032,
  "natural_increase_share": 2.41,
  "migration_estimate": 5780.0,
  "migration_rate": 18.3,
  "natural_increase_rate": -32.4,
  "total_demographic_balance": -4439.0,
  "demographic_balance_rate": -14.1,
  "vrp_per_capita": 219.7,
  "salary_to_vrp_ratio": 0.53,
  "population_moving_average": 3161000.0,
  "unemployment_moving_average": 3.8,
  "natural_increase_moving_average": -10850.0,
  "average_salary_moving_average": 112.9,
  "vrp_moving_average": 661000000.0,
  "migration_balance_moving_average": 14.8
}
```

Meaning of the most important derived fields:

- `population_growth_rate`: yearly population growth
- `salary_growth_rate`: yearly growth of the real wage index
- `vrp_growth_rate`: yearly VRP growth
- `vrp_per_capita`: `vrp / population`
- `migration_rate`: migration balance coefficient from source data
- `natural_increase_rate`: `natural_increase / population * 10000`
- `demographic_balance_rate`: `natural_increase_rate + migration_rate`

---

## 7. Region trends and correlations

### `GET /api/analytics/region/{region_id}/trends`

Linear trend parameters:

```json
{
  "metric": "vrp",
  "slope": 15423122.4,
  "intercept": -30877100000.0
}
```

Returned metrics currently include:

- `population`
- `unemployment_rate`
- `natural_increase`
- `average_salary`
- `vrp`
- `migration_balance`
- `salary_growth_rate`
- `vrp_growth_rate`

### `GET /api/analytics/region/{region_id}/correlation`

Backward-compatible simple response:

```json
{
  "region_id": 63,
  "correlation": -0.42
}
```

This is `population <-> unemployment`.

### `GET /api/analytics/region/{region_id}/correlations`

Extended response:

```json
{
  "region_id": 63,
  "population_unemployment_correlation": -0.42,
  "natural_increase_population_growth_correlation": 0.53,
  "natural_increase_unemployment_correlation": -0.27
}
```

---

## 8. Normalization

### `GET /api/analytics/normalized/economic?year=2023`

Returns one-year economic cross-section for regions:

- `salary_growth_rate`
- `vrp_per_capita`
- `unemployment_rate`
- z-score fields
- min-max fields

Response item:

```json
{
  "region_id": 63,
  "region_name": "Самарская область",
  "year": 2023,
  "salary_growth_rate": 0.041,
  "vrp_per_capita": 219.7,
  "unemployment_rate": 3.6,
  "z_salary_growth_rate": 0.28,
  "z_vrp_per_capita": 0.13,
  "z_unemployment_rate": -0.52,
  "minmax_salary_growth_rate": 0.61,
  "minmax_vrp_per_capita": 0.57,
  "minmax_unemployment_rate": 0.62
}
```

### `GET /api/analytics/normalized/demographic?year=2023`

Returns one-year demographic cross-section for regions:

- `population_growth_rate`
- `natural_increase_rate`
- `migration_rate`
- z-score fields
- min-max fields

---

## 9. Composite indices

### `GET /api/analytics/composite-index/economic`

Query params:

- `year` required
- `limit` optional, default `10`
- `w1` optional, default `0.35`
- `w2` optional, default `0.35`
- `w3` optional, default `0.30`

Formula:

```text
composite_economic_index =
    w1 * z(salary_growth_rate)
  + w2 * z(vrp_per_capita)
  - w3 * z(unemployment_rate)
```

Response item:

```json
{
  "region_id": 63,
  "region_name": "Самарская область",
  "year": 2023,
  "composite_economic_index": 0.27,
  "salary_growth_rate": 0.041,
  "vrp_per_capita": 219.7,
  "unemployment_rate": 3.6
}
```

### `GET /api/analytics/composite-index/demographic`

Query params:

- `year` required
- `limit` optional, default `10`
- `w1` optional, default `0.34`
- `w2` optional, default `0.33`
- `w3` optional, default `0.33`

Formula:

```text
composite_demographic_index =
    w1 * z(population_growth_rate)
  + w2 * z(natural_increase_rate)
  + w3 * z(migration_rate)
```

---

## 10. Rankings

All ranking endpoints accept:

- `year` required
- `limit` optional, default `10`

Available endpoints:

- `GET /api/analytics/rankings/lowest-unemployment`
- `GET /api/analytics/rankings/population-growth`
- `GET /api/analytics/rankings/unemployment-decline`
- `GET /api/analytics/rankings/natural-increase`
- `GET /api/analytics/rankings/natural-decrease`
- `GET /api/analytics/rankings/natural-increase-improvement`
- `GET /api/analytics/rankings/salary`
- `GET /api/analytics/rankings/salary-growth`
- `GET /api/analytics/rankings/vrp-per-capita`
- `GET /api/analytics/rankings/migration-attractiveness`
- `GET /api/analytics/rankings/demographic-balance`

Backward compatibility:

- `GET /api/analytics/top-unemployment`

This is the same as `rankings/lowest-unemployment`.

---

## 11. TypeScript types

```ts
export type AnalyticsDatasetItem = {
  region_id: number;
  region_name: string;
  year: number;
  population: number | null;
  unemployment_rate: number | null;
  natural_increase: number | null;
  migration_balance: number | null;
  average_salary: number | null;
  vrp: number | null;
};

export type RegionAnalyticsMetrics = {
  year: number;
  population_growth_rate: number | null;
  salary_growth_rate: number | null;
  vrp_growth_rate: number | null;
  unemployment_delta: number | null;
  natural_increase_delta: number | null;
  adjusted_population_change: number | null;
  natural_increase_share: number | null;
  migration_estimate: number | null;
  migration_rate: number | null;
  natural_increase_rate: number | null;
  total_demographic_balance: number | null;
  demographic_balance_rate: number | null;
  vrp_per_capita: number | null;
  salary_to_vrp_ratio: number | null;
  population_moving_average: number | null;
  unemployment_moving_average: number | null;
  natural_increase_moving_average: number | null;
  average_salary_moving_average: number | null;
  vrp_moving_average: number | null;
  migration_balance_moving_average: number | null;
};
```

---

## 12. Quick frontend examples

Build dictionaries:

```ts
const [regionsRes, indicatorsRes] = await Promise.all([
  fetch("/api/regions"),
  fetch("/api/indicators"),
]);

const regions = await regionsRes.json();
const indicators = await indicatorsRes.json();
const indicatorMap = new Map(indicators.map((item: any) => [item.code, item.id]));
```

Raw series for migration:

```ts
const migrationId = indicatorMap.get("MIGRATION_BALANCE_RATE");
const url = `/api/values?indicator_id=${migrationId}&region_id=${regionId}&period=year`;
const series = await (await fetch(url)).json();
```

Dashboard dataset:

```ts
const data = await (
  await fetch("/api/analytics/dataset?start_year=2004&end_year=2023")
).json();
```

Economic leaderboard:

```ts
const top = await (
  await fetch("/api/analytics/composite-index/economic?year=2023&limit=15")
).json();
```

Regional derived metrics:

```ts
const metrics = await (
  await fetch(`/api/analytics/region/${regionId}/metrics`)
).json();
```
