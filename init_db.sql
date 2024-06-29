-- 创建数据库
CREATE DATABASE GymBookingSystem;
GO

USE GymBookingSystem;
GO

-- 创建用户表
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(120) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "is_staff" BOOLEAN DEFAULT FALSE,
    "is_active" BOOLEAN DEFAULT TRUE,
    "created_at" TIMESTAMP NOT NULL,
    "updated_at" TIMESTAMP NOT NULL
);

-- 创建用户表的索引
CREATE INDEX IF NOT EXISTS "ix_users_username" ON "users" ("username");
CREATE INDEX IF NOT EXISTS "ix_users_email" ON "users" ("email");

-- 创建个人资料表
CREATE TABLE Profile (
    ProfileId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    FullName VARCHAR(50),
    Department VARCHAR(50),
    PreferredSports VARCHAR(100),
    PreferredTime VARCHAR(100),
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES [User](UserId)
);

-- 创建运动场馆表
CREATE TABLE SportVenue (
    SportVenueId INT PRIMARY KEY IDENTITY(1,1),
    SportVenueName VARCHAR(50) NOT NULL,
    Location VARCHAR(100) NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE()
);

-- 创建运动场馆表的索引
CREATE INDEX IX_SportVenue_SportVenueName ON SportVenue(SportVenueName);

-- 创建具体场馆表
CREATE TABLE Venue (
    VenueId INT PRIMARY KEY IDENTITY(1,1),
    SportVenueId INT NOT NULL,
    VenueName VARCHAR(50) NOT NULL,
    Capacity INT NOT NULL,
    Notice TEXT,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (SportVenueId) REFERENCES SportVenue(SportVenueId)
);

-- 创建具体场馆表的索引
CREATE INDEX IX_Venue_VenueName ON Venue(VenueName);

-- 创建设施表
CREATE TABLE Facility (
    FacilityId INT PRIMARY KEY IDENTITY(1,1),
    VenueId INT NOT NULL,
    FacilityName VARCHAR(50) NOT NULL,
    Description TEXT,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (VenueId) REFERENCES Venue(VenueId)
);

-- 创建预约时间段表
CREATE TABLE ReservationTimeSlot (
    TimeSlotId INT PRIMARY KEY IDENTITY(1,1),
    VenueId INT NOT NULL,
    Date DATE NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (VenueId) REFERENCES Venue(VenueId)
);

-- 创建预约时间段表的索引
CREATE INDEX IX_ReservationTimeSlot_Date ON ReservationTimeSlot(Date);

-- 创建预约表
CREATE TABLE Reservation (
    ReservationId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    TimeSlotId INT NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT '已预约',
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES [User](UserId),
    FOREIGN KEY (TimeSlotId) REFERENCES ReservationTimeSlot(TimeSlotId)
);

-- 创建预约表的组合索引
CREATE INDEX IX_Reservation_UserId_TimeSlotId ON Reservation(UserId, TimeSlotId);

-- 创建等候列表表
CREATE TABLE WaitingList (
    WaitingId INT PRIMARY KEY IDENTITY(1,1),
    ReservationId INT NOT NULL,
    UserId INT NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ReservationId) REFERENCES Reservation(ReservationId),
    FOREIGN KEY (UserId) REFERENCES [User](UserId)
);

-- 创建反馈表
CREATE TABLE Feedback (
    FeedbackId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    Title VARCHAR(100) NOT NULL,
    Content TEXT NOT NULL,
    Reply TEXT,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES [User](UserId)
);

-- 创建通知表
CREATE TABLE Notification (
    NotificationId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    Title VARCHAR(100) NOT NULL,
    Content TEXT NOT NULL,
    Type VARCHAR(20) NOT NULL,
    IsRead BIT NOT NULL DEFAULT 0,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES [User](UserId)
);

-- 创建领导预留时间表
CREATE TABLE LeaderReservedTime (
    ReservedTimeId INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    VenueId INT NOT NULL,
    DayOfWeek INT NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES [User](UserId),
    FOREIGN KEY (VenueId) REFERENCES Venue(VenueId)
);

-- 创建领导预留时间表的组合索引
CREATE INDEX IX_LeaderReservedTime_UserId_VenueId ON LeaderReservedTime(UserId, VenueId);

-- 初始化角色数据
INSERT INTO [User] (Username, Password, Email, Phone, Role)
VALUES ('admin', 'password', 'admin@example.com', '123456789', 'Admin');

-- 初始化运动场馆数据
INSERT INTO SportVenue (SportVenueName, Location)
VALUES ('篮球馆', '1号体育馆'),
       ('足球场', '2号体育馆'),
       ('网球场', '3号体育馆');

-- 初始化具体场馆数据
INSERT INTO Venue (SportVenueId, VenueName, Capacity, Notice)
VALUES (1, '篮球馆1', 50, '预约须知:请带好运动鞋和水'),
       (1, '篮球馆2', 40, '预约须知:请勿在场地吸烟'),
       (2, '足球场1', 30, '预约须知:请勿带食物和饮料入场'),
       (3, '网球场1', 20, '预约须知:请遵守场地秩序');

-- 初始化设施数据
INSERT INTO Facility (VenueId, FacilityName, Description)
VALUES (1, '淋浴间', '位于篮球馆1旁边'),
       (2, '更衣室', '位于篮球馆2旁边'),
       (3, '储物柜', '位于足球场1入口处'),
       (4, '休息区', '位于网球场1旁边');