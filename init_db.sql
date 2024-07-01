-- 创建数据库
CREATE DATABASE fitness_venue_booking_dev;

-- 切换到新创建的数据库
\c fitness_venue_booking_dev;

-- 创建用户表
CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20) NOT NULL,
  role SMALLINT NOT NULL DEFAULT 0,
  is_leader BOOLEAN NOT NULL DEFAULT false,
  full_name VARCHAR(50),
  department VARCHAR(50),
  preferred_sports VARCHAR(100),
  preferred_time VARCHAR(100),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建运动场馆表
CREATE TABLE sport_venue (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  location VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建具体场馆表
CREATE TABLE venue (
  id SERIAL PRIMARY KEY,
  sport_venue_id INTEGER NOT NULL REFERENCES sport_venue(id),
  name VARCHAR(50) NOT NULL,
  capacity INTEGER NOT NULL,
  notice TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建设施表
CREATE TABLE facility (
  id SERIAL PRIMARY KEY,
  venue_id INTEGER NOT NULL REFERENCES venue(id),
  name VARCHAR(50) NOT NULL,
  description TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建预约时间段表
CREATE TABLE reservation_time_slot (
  id SERIAL PRIMARY KEY,
  venue_id INTEGER NOT NULL REFERENCES venue(id),
  date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建预约表
CREATE TABLE reservation (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  time_slot_id INTEGER NOT NULL REFERENCES reservation_time_slot(id),
  status VARCHAR(20) NOT NULL DEFAULT 'RESERVED',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建等候列表表
CREATE TABLE waiting_list (
  id SERIAL PRIMARY KEY,
  reservation_id INTEGER NOT NULL REFERENCES reservation(id),
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建反馈表
CREATE TABLE feedback (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  title VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  reply TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建通知表
CREATE TABLE notification (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  title VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  type VARCHAR(20) NOT NULL,
  is_read BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建领导预留时间表
CREATE TABLE leader_reserved_time (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user"(id),
  venue_id INTEGER NOT NULL REFERENCES venue(id),
  day_of_week SMALLINT NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 创建VenueStatus枚举类型
CREATE TYPE VenueStatus AS ENUM ('open', 'closed', 'maintenance');

-- 修改具体场馆表,增加status字段
ALTER TABLE venue
ADD COLUMN status VenueStatus NOT NULL DEFAULT 'open';

-- 创建ReservationStatus枚举类型
CREATE TYPE ReservationStatus AS ENUM ('pending', 'confirmed', 'cancelled');

-- 修改预约表,更改status字段类型为ReservationStatus
ALTER TABLE reservation
ALTER COLUMN status TYPE ReservationStatus USING status::ReservationStatus;

-- 更新预约表中status字段的默认值
ALTER TABLE reservation
ALTER COLUMN status SET DEFAULT 'pending';


-- 插入示例数据
-- 插入用户数据
INSERT INTO "user" (username, password, email, phone, role, is_leader, full_name, department, preferred_sports, preferred_time)
VALUES
  ('john_doe', 'password123', 'john@example.com', '1234567890', 0, false, 'John Doe', 'IT', 'Basketball, Swimming', 'Evening'),
  ('jane_smith', 'qwerty', 'jane@example.com', '9876543210', 0, false, 'Jane Smith', 'HR', 'Yoga, Running', 'Morning'),
  ('admin', 'admin123', 'admin@example.com', '1111111111', 1, true, 'Admin User', 'Administration', NULL, NULL);

-- 插入运动场馆数据  
INSERT INTO sport_venue (name, location)
VALUES
  ('Basketball Court', '1st Floor, Building A'),
  ('Swimming Pool', '2nd Floor, Building B'),
  ('Yoga Studio', '3rd Floor, Building C'),
  ('Running Track', 'Outdoor Area');

-- 插入具体场馆数据
INSERT INTO venue (sport_venue_id, name, capacity, notice)
VALUES
  (1, 'Court A', 20, 'Please bring your own basketball'),
  (1, 'Court B', 20, 'Please bring your own basketball'),
  (2, 'Lane 1', 10, 'Please bring your own swimming cap'),
  (2, 'Lane 2', 10, 'Please bring your own swimming cap'),
  (3, 'Studio 1', 15, 'Please bring your own yoga mat'),
  (4, 'Track 1', 30, 'Please run in counter-clockwise direction');

-- 插入设施数据  
INSERT INTO facility (venue_id, name, description)
VALUES
  (1, 'Shower Room', 'Male shower room'),
  (1, 'Locker Room', 'Male locker room'),
  (2, 'Shower Room', 'Female shower room'),
  (2, 'Locker Room', 'Female locker room'),
  (3, 'Changing Room', 'Unisex changing room'),
  (4, 'Water Fountain', 'Drinking water fountain');

-- 插入预约时间段数据
INSERT INTO reservation_time_slot (venue_id, date, start_time, end_time)
VALUES
  (1, '2023-06-01', '09:00:00', '10:00:00'),
  (1, '2023-06-01', '10:00:00', '11:00:00'),
  (2, '2023-06-01', '14:00:00', '15:00:00'),
  (2, '2023-06-01', '15:00:00', '16:00:00'),
  (3, '2023-06-02', '08:00:00', '09:00:00'),
  (4, '2023-06-02', '18:00:00', '19:00:00');

-- 插入预约数据
INSERT INTO reservation (user_id, time_slot_id, status)
VALUES
  (1, 1, 'RESERVED'),
  (2, 3, 'RESERVED'),
  (1, 5, 'RESERVED');

-- 插入等候列表数据
INSERT INTO waiting_list (reservation_id, user_id)
VALUES
  (1, 2),
  (2, 1);

-- 插入反馈数据
INSERT INTO feedback (user_id, title, content, reply)
VALUES
  (1, 'Great facilities', 'The basketball courts are well-maintained. Thank you!', 'Thank you for your feedback. We are glad you enjoyed our facilities.'),
  (2, 'Improve cleanliness', 'The changing rooms could be cleaner. Please look into it.', NULL);

-- 插入通知数据
INSERT INTO notification (user_id, title, content, type, is_read)
VALUES
  (1, 'Reservation Confirmed', 'Your reservation for Basketball Court on 2023-06-01 at 09:00 has been confirmed.', 'RESERVATION', true),
  (2, 'Feedback Received', 'Thank you for your feedback. We will address your concerns as soon as possible.', 'FEEDBACK', false);

-- 插入领导预留时间数据
INSERT INTO leader_reserved_time (user_id, venue_id, day_of_week, start_time, end_time)
VALUES
  (3, 1, 1, '14:00:00', '15:00:00'),
  (3, 2, 3, '10:00:00', '11:00:00');

-- 创建索引
CREATE UNIQUE INDEX idx_user_username ON "user"(username);
CREATE UNIQUE INDEX idx_user_email ON "user"(email);
CREATE UNIQUE INDEX idx_sport_venue_name ON sport_venue(name);
CREATE INDEX idx_venue_name ON venue(name);
CREATE INDEX idx_reservation_time_slot_date ON reservation_time_slot(date);
CREATE INDEX idx_reservation_user_id_time_slot_id ON reservation(user_id, time_slot_id);
CREATE INDEX idx_leader_reserved_time_user_id_venue_id ON leader_reserved_time(user_id, venue_id);