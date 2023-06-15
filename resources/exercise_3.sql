-- Create the Data Warehouse schema
CREATE SCHEMA dw;

-- Integrate the Postgis extension
CREATE EXTENSION postgis;

-- Integrate the Uber H3 extension
CREATE EXTENSION h3;

-- Create Dim Users table
CREATE TABLE dw.dim_user (
  user_id SERIAL PRIMARY KEY,
  customer_nk TEXT NOT NULL,
  email_address VARCHAR(255) NOT,
  is_guest_customer BIT NOT NULL,
  guest_customer_label VARCHAR(255) NOT NULL,
  customer_type VARCHAR(50) NOT NULL,
  gender VARCHAR(50) NOT NULL,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL,
  phone_contact_country_code VARCHAR(3) NOT NULL,
  phone_contact_extension VARCHAR(5) NOT NULL,
  phone_contact_number SMALLINT NOT NULL,
  record_valid_from TIMESTAMP NOT NULL,
  record_valid_to TIMESTAMP NOT NULL,
  is_record_valid BIT NOT NULL
);

COMMENT ON COLUMN dw.dim_user.customer_nk IS 'The customers natural key';
COMMENT ON COLUMN dw.dim_user.email_address IS 'The customers email address';
COMMENT ON COLUMN dw.dim_user.is_guest_customer IS 'Is the Customer a guest customer or, an authenticated customer';
COMMENT ON COLUMN dw.dim_user.guest_customer_label IS 'String representing the is_guest_customer flag';
COMMENT ON COLUMN dw.dim_user.customer_type IS 'String representing the customers type, Registered or Unregistered';
COMMENT ON COLUMN dw.dim_user.gender IS 'The customers gender';
COMMENT ON COLUMN dw.dim_user.first_name IS 'The customers first name';
COMMENT ON COLUMN dw.dim_user.last_name IS 'The customers last name';
COMMENT ON COLUMN dw.dim_user.username IS 'The customers user name';
COMMENT ON COLUMN dw.dim_user.phone_contact_country_code IS 'The customers phone contact country code';
COMMENT ON COLUMN dw.dim_user.phone_contact_extension IS 'The customers phone contact extension';
COMMENT ON COLUMN dw.dim_user.phone_contact_number IS 'The customers phone contact number';
COMMENT ON COLUMN dw.dim_user.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.dim_user.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.dim_user.is_record_valid IS 'True if the record is not the most recent/active';

-- Create Dim Locations table
CREATE TABLE dw.dim_location (
  location_id SERIAL PRIMARY KEY,
  country_name VARCHAR(255) NOT NULL,
  region_name VARCHAR(255) NOT NULL,
  city_name VARCHAR(255) NOT NULL,
  coordinates GEOGRAPHY(POINT) NOT NULL,
  wof_level_0_polygon GEOMETRY NOT NULL,
  wof_level_1_polygon GEOMETRY NOT NULL,
  wof_level_2_polygon GEOMETRY NOT NULL,
  record_valid_from TIMESTAMP NOT NULL,
  record_valid_to TIMESTAMP NOT NULL,
  is_record_valid BIT NOT NULL
);

COMMENT ON COLUMN dw.dim_location.country_name IS 'The associated country name';
COMMENT ON COLUMN dw.dim_location.region_name IS 'The associated region name';
COMMENT ON COLUMN dw.dim_location.city_name IS 'The associated city name';
COMMENT ON COLUMN dw.dim_location.coordinates IS 'The associated PostGIS coordinates instance';
COMMENT ON COLUMN dw.dim_location.wof_level_0_polygon IS 'The associated WOF polygon for administrative region level 0';
COMMENT ON COLUMN dw.dim_location.wof_level_1_polygon IS 'The associated WOF polygon for administrative region level 1';
COMMENT ON COLUMN dw.dim_location.wof_level_2_polygon IS 'The associated WOF polygon for administrative region level 2';
COMMENT ON COLUMN dw.dim_location.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.dim_location.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.dim_location.is_record_valid IS 'True if the record is not the most recent/active';

-- Add a Postgis spatial index to the coordinates attribute
CREATE INDEX gix_dim_location_coordinates ON dw.dim_location USING GIST (coordinates);

-- Create Dim Spatial Index for storing H3 object instances table
CREATE TABLE dw.dim_spatial_index (
  spatial_index_id H3INDEX PRIMARY KEY,
  h3_hex VARCHAR(255) NOT NULL,
  hex_resolution INTEGER NOT NULL,
  geom GEOMETRY (POLYGON, 4326) NOT NULL,
  record_valid_from TIMESTAMP NOT NULL COMMENT 'The records start date',
  record_valid_to TIMESTAMP NOT NULL COMMENT 'The records end date',
  is_record_valid BIT NOT NULL COMMENT 'True if the record is not the most recent/active'

  CONSTRAINT ck_resolution CHECK (hex_resolution >= 0 AND hex_resolution <= 15)
);

COMMENT ON COLUMN dw.dim_spatial_index.h3_hex IS 'The associated H3 polygon''s HEX';
COMMENT ON COLUMN dw.dim_spatial_index.hex_resolution IS 'The H3 polygon''s resolution';
COMMENT ON COLUMN dw.dim_spatial_index.geom IS 'The associated HE polygon''s geometry object';
COMMENT ON COLUMN dw.dim_spatial_index.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.dim_spatial_index.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.dim_spatial_index.is_record_valid IS 'True if the record is not the most recent/active';

-- Create Dim Date table
CREATE TABLE dw.dim_date (
  date_id SERIAL PRIMARY KEY,
  date_actual DATE NOT NULL,
  day_of_week INTEGER NOT NULL,
  day_of_month INTEGER NOT NULL,
  day_of_year INTEGER NOT NULL,
  days_to_month_end INTEGER NOT NULL,
  days_to_year_end INTEGER NOT NULL,
  is_weekend BIT NOT NULL,
  weekend_label STRING NOT NULL,
  is_last_day_of_month BIT NOT NULL,
  last_day_of_month_label STRING NOT NULL,
  week_start_date DATE NOT NULL,
  week_end_date DATE NOT NULL,
  week_of_month INTEGER NOT NULL,
  week_of_year INTEGER NOT NULL,
  month_number INTEGER NOT NULL,
  month_start_date DATE NOT NULL,
  month_end_date DATE NOT NULL,
  quarter_number INTEGER NOT NULL,
  quarter_start_date DATE NOT NULL,
  quarter_end_date DATE NOT NULL,
  year_number INTEGER NOT NULL,
  is_leap_year BIT NOT NULL,
  leap_year_label STRING NOT NULL,
  fiscal_quarter_number INTEGER NOT NULL,
  fiscal_year_number INTEGER NOT NULL,
  season_start_date DATE NOT NULL,
  season_end_date DATE NOT NULL,
  season_northern STRING NOT NULL,
  season_southern STRING NOT NULL,
  record_valid_from TIMESTAMP NOT NULL,
  record_valid_to TIMESTAMP NOT NULL,
  is_record_valid BIT NOT NULL
);

COMMENT ON COLUMN dw.dim_date.date_actual IS 'The actual date object';
COMMENT ON COLUMN dw.dim_date.day_of_week IS 'The day of week in string format where Monday is 1';
COMMENT ON COLUMN dw.dim_date.day_of_month IS 'The day of month in integer format';
COMMENT ON COLUMN dw.dim_date.day_of_year IS 'The day of year in integer format';
COMMENT ON COLUMN dw.dim_date.days_to_month_end IS 'The number of days until the month ends';
COMMENT ON COLUMN dw.dim_date.days_to_year_end IS 'The number of days until the year ends';
COMMENT ON COLUMN dw.dim_date.is_weekend IS 'Is the date in a weekend';
COMMENT ON COLUMN dw.dim_date.weekend_label IS 'String representing if the date in a weekend';
COMMENT ON COLUMN dw.dim_date.is_last_day_of_month IS 'Is the last day of the referred month';
COMMENT ON COLUMN dw.dim_date.last_day_of_month_label IS 'String representing if the date is the last day of the referred month';
COMMENT ON COLUMN dw.dim_date.week_start_date IS 'The date''s week start date';
COMMENT ON COLUMN dw.dim_date.week_end_date IS '"The date''s week end date';
COMMENT ON COLUMN dw.dim_date.week_of_month IS 'An integer representing the week''s number within the month';
COMMENT ON COLUMN dw.dim_date.week_of_year IS 'An integer representing the week''s number within the year';
COMMENT ON COLUMN dw.dim_date.month_number IS 'An integer representing the month''s number within the year';
COMMENT ON COLUMN dw.dim_date.month_start_date IS '"The month''s start date';
COMMENT ON COLUMN dw.dim_date.month_end_date IS 'The month''s end date';
COMMENT ON COLUMN dw.dim_date.quarter_number IS 'An integer representing the quarter''s number within the year';
COMMENT ON COLUMN dw.dim_date.quarter_start_date IS '"The quarter''s start date in YYYY-MM-DD format';
COMMENT ON COLUMN dw.dim_date.quarter_end_date IS 'The quarter''s end date in YYYY-MM-DD format';
COMMENT ON COLUMN dw.dim_date.year_number IS 'An integer representing the year''s e.g. 2021';
COMMENT ON COLUMN dw.dim_date.is_leap_year IS 'Is the year a leap (has 365 days)';
COMMENT ON COLUMN dw.dim_date.leap_year_label IS 'String representing if the year a leap (has 365 days)';
COMMENT ON COLUMN dw.dim_date.fiscal_quarter_number IS 'The fiscal quarter''s number';
COMMENT ON COLUMN dw.dim_date.fiscal_year_number IS 'The fiscal year''s number';
COMMENT ON COLUMN dw.dim_date.season_start_date IS 'The period''s season start date';
COMMENT ON COLUMN dw.dim_date.season_end_date IS 'The period''s season end date';
COMMENT ON COLUMN dw.dim_date.season_northern IS 'The period''s season considering the Northern hemisphere';
COMMENT ON COLUMN dw.dim_date.season_southern IS 'The period''s season considering the Southern hemisphere';
COMMENT ON COLUMN dw.dim_date.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.dim_date.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.dim_date.is_record_valid IS 'True if the record is not the most recent/active';

-- Create Dim Time table
CREATE TABLE dw.dim_time (
  time_id SERIAL PRIMARY KEY,
  hour_24 INTEGER NOT NULL,
  time_standard_code STRING NOT NULL,
  minute INTEGER NOT NULL,
  is_first_half_hour_band BIT NOT,
  first_half_hour_band_label STRING NOT NULL,
  second INTEGER NOT NULL,
  record_valid_from TIMESTAMP NOT NULL,
  record_valid_to TIMESTAMP NOT NULL,
  is_record_valid BOOLEAN NOT NULL
);

COMMENT ON COLUMN dw.dim_time.hour_24 IS 'The hour of day in integer format under a 24-hour cycle';
COMMENT ON COLUMN dw.dim_time.time_standard_code IS 'The time standard code in meridiam, is the time AM or PM';
COMMENT ON COLUMN dw.dim_time.minute IS 'The minute of day in integer format';
COMMENT ON COLUMN dw.dim_time.is_first_half_hour_band IS 'Indicator which assumes the value True if the minute is in the hour''s first half-hour band, false otherswise';
COMMENT ON COLUMN dw.dim_time.first_half_hour_band_label IS 'String representing if the minute is in the hour''s first half-hour band';
COMMENT ON COLUMN dw.dim_time.second IS 'The second of day in integer format';
COMMENT ON COLUMN dw.dim_time.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.dim_time.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.dim_time.is_record_valid IS 'True if the record is not the most recent/active';

-- Create Fact_Checkins table
CREATE TABLE dw.fact_checkin (
  checkin_id SERIAL PRIMARY KEY,
  user_id INT REFERENCES dw.dim_user(user_id),
  checkin_location_id INT REFERENCES dw.dim_location(location_id),
  spatial_index_id INT REFERENCES dw.dim_spatial_index(dim_spatial_index)
  checkin_standard_date_id INT REFERENCES dw.dim_date(date_id),
  checkin_standard_time_id INT REFERENCES dw.dim_time(time_id),
  checkin_local_date_id INT REFERENCES dw.dim_date(date_id),
  checkin_local_time_id INT REFERENCES dw.dim_time(time_id),
  record_valid_from TIMESTAMP NOT NULL COMMENT 'The records start date',
  record_valid_to TIMESTAMP NOT NULL COMMENT 'The records end date'
);

CREATE INDEX idx_fact_checkin_user_id_date_id ON dw.fact_checkin (user_id, checkin_standard_date_id);

COMMENT ON COLUMN dw.fact_checkin.user_id IS 'The associated User Dimension Foreign Key';
COMMENT ON COLUMN dw.fact_checkin.checkin_location_id IS 'The associated Location Dimension Foreign Key';
COMMENT ON COLUMN dw.fact_checkin.spatial_index_id IS 'The associated Spatial Index Dimension Foreign Key';
COMMENT ON COLUMN dw.fact_checkin.checkin_standard_date_id IS 'The associated Date Dimension Foreign Key under a Standard timezone Role-Play';
COMMENT ON COLUMN dw.fact_checkin.checkin_standard_time_id IS 'The associated Time Dimension Foreign Key under a Standard timezone Role-Play';
COMMENT ON COLUMN dw.fact_checkin.checkin_local_date_id IS 'The associated Date Dimension Foreign Key under a Local timezone Role-Play';
COMMENT ON COLUMN dw.fact_checkin.record_valid_to IS 'The associated Time Dimension Foreign Key under a Local timezone Role-Play';
COMMENT ON COLUMN dw.fact_checkin.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.fact_checkin.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.fact_checkin.is_record_valid IS 'True if the record is not the most recent/active';

-- Create Fact Checkin Aggregates for H3 resolution 9 considering the Standard timezone
CREATE TABLE dw.fact_checkin_h3_res9_agg (
  spatial_index_id INT REFERENCES dim_spatial_index(spatial_index_id),
  checkin_standard_date_id INT REFERENCES dw.dim_date(date_id),
  checkin_qty INTEGER NOT NULL,
  unique_user_qty INTEGER NOT NULL,
  record_valid_from TIMESTAMP NOT NULL COMMENT 'The records start date',
  record_valid_to TIMESTAMP NOT NULL COMMENT 'The records end date'
);

CREATE INDEX idx_fact_checkin_h3_res9_agg_id_date_id ON dw.fact_checkin_h3_res9_agg (checkin_location_id, checkin_standard_date_id);

COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.user_id IS 'The associated User Dimension Foreign Key';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.spatial_index_id IS 'The associated Spatial Index Dimension Foreign Key';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.checkin_standard_date_id IS 'The associated Date Dimension Foreign Key under a Standard timezone Role-Play';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.checkin_qty IS 'The associated number of checkins for the specified spatial index and date';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.unique_user_qty IS 'The associated number of unique users for the specified spatial index and date';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.record_valid_from IS 'The records start date';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.record_valid_to IS 'The records end date';
COMMENT ON COLUMN dw.fact_checkin_h3_res9_agg.is_record_valid IS 'True if the record is not the most recent/active';