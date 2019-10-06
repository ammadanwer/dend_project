DROP_DIM_COUNTY = "DROP TABLE IF EXISTS dim_county;"
DROP_FACT_POVERTY = "DROP TABLE IF EXISTS fact_poverty;"
DROP_FACT_UNEMPLOYEMENT = "DROP TABLE IF EXISTS fact_unemployement;"

CREATE_DIM_COUNTY = """
CREATE IF NOT EXISTS TABLE dim_county
(
	fips_id TEXT NOT NULL
		CONSTRAINT DIM_COUNTY_pk
			PRIMARY KEY,
	name TEXT,
	state TEXT
);
"""

CREATE_FACT_POVERTY = """
CREATE IF NOT EXISTS TABLE IF NOT EXISTS fact_poverty
(
	id SERIAL NOT NULL
		CONSTRAINT fact_poverty_pk
			PRIMARY KEY,
	fips_id TEXT,
	year INTEGER,
	percentage DOUBLE PRECISION
);
"""

CREATE_FACT_UNEMPLOYEMENT = """
CREATE TABLE IF NOT EXISTS fact_unemployment
(
	id SERIAL NOT NULL
		CONSTRAINT fact_unemployment_pk
			PRIMARY KEY,
	fips_id TEXT,
	year INTEGER,
	percentage DOUBLE PRECISION
);
"""

GET_STATE_DATA = """
SELECT c.*,
       p.percentage AS poverty_percentage,
       u.percentage AS unemployment_percentage
FROM dim_county c
INNER JOIN fact_poverty p ON c.fips_id = p.fips_id
INNER JOIN fact_unemployment u ON c.fips_id = u.fips_id
WHERE mod(c.fips_id, 1000)=0 AND state != 'US';
"""

GET_COUNTY_DATA = """
SELECT c.*,
       p.percentage AS poverty_percentage,
       u.percentage AS unemployment_percentage
FROM dim_county c
INNER JOIN fact_poverty p ON c.fips_id = p.fips_id
INNER JOIN fact_unemployment u ON c.fips_id = u.fips_id
WHERE LOWER(c.state) = '{state_code}';
"""

create_table_queries = [CREATE_DIM_COUNTY, CREATE_FACT_POVERTY, CREATE_FACT_UNEMPLOYEMENT]

drop_table_queries = [DROP_DIM_COUNTY, DROP_FACT_POVERTY, DROP_FACT_UNEMPLOYEMENT]
