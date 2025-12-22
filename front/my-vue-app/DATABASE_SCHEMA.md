# 备件管理系统 - 数据库设计

## 1. 核心实体关系图 (ER Diagram)

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│    User      │        │   Station    │        │    Part      │
├──────────────┤        ├──────────────┤        ├──────────────┤
│ id (PK)      │◄──────►│ id (PK)      │◄──────►│ id (PK)      │
│ name         │ N:1    │ name         │ 1:N    │ name         │
│ email        │        │ desc         │        │ model        │
│ password     │        │ location     │        │ location     │
│ stationId(FK)│        │ created_at   │        │ qty          │
│ created_at   │        │ updated_at   │        │ alarmQty     │
│ updated_at   │        │              │        │ procurementDays
└──────────────┘        └──────────────┘        │ stationId(FK)│
                                                │ imageUrl     │
                                                │ desc         │
                                                │ created_by   │
                                                │ created_at   │
                                                │ updated_at   │
                                                │ updated_by   │
                                                └──────────────┘
```

## 2. 数据库表设计

### 2.1 用户表 (users)

用途: 存储所有系统用户的信息

| 字段名 | 数据类型 | 约束 | 说明 |
|------|---------|------|------|
| id | UUID/String | PRIMARY KEY | 用户唯一标识符 |
| name | VARCHAR(100) | NOT NULL | 用户名称/昵称 |
| email | VARCHAR(255) | NOT NULL, UNIQUE | 用户邮箱（登录用） |
| password | VARCHAR(255) | NOT NULL | 密码哈希值（使用 bcrypt） |
| stationId | UUID/String | NOT NULL, FK → stations(id) | 用户所属场站 |
| role | ENUM('user', 'admin') | NOT NULL, DEFAULT 'user' | 用户角色 |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | 账户是否激活 |
| last_login | DATETIME | NULLABLE | 最后登录时间 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引:**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stationId ON users(stationId);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**示例数据:**
```json
{
  "id": "u1",
  "name": "张三",
  "email": "zhangsan@company.com",
  "password": "$2b$10$...",
  "stationId": "station-1",
  "role": "user",
  "is_active": true,
  "last_login": "2025-12-07T10:30:00Z",
  "created_at": "2025-01-01T08:00:00Z",
  "updated_at": "2025-12-07T10:30:00Z"
}
```

---

### 2.2 场站表 (stations)

用途: 存储所有维修/运维场站的信息

| 字段名 | 数据类型 | 约束 | 说明 |
|------|---------|------|------|
| id | UUID/String | PRIMARY KEY | 场站唯一标识符 |
| name | VARCHAR(100) | NOT NULL, UNIQUE | 场站名称 (如: station-1, station-2) |
| display_name | VARCHAR(255) | NOT NULL | 场站显示名称 (如: "华东地区生产中心") |
| location | VARCHAR(255) | NULLABLE | 场站地理位置 |
| phone | VARCHAR(20) | NULLABLE | 场站联系电话 |
| manager | VARCHAR(100) | NULLABLE | 场站负责人 |
| manager_email | VARCHAR(255) | NULLABLE | 负责人邮箱 |
| description | TEXT | NULLABLE | 场站描述信息 |
| is_active | BOOLEAN | NOT NULL, DEFAULT true | 场站是否启用 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引:**
```sql
CREATE UNIQUE INDEX idx_stations_name ON stations(name);
CREATE INDEX idx_stations_is_active ON stations(is_active);
```

**示例数据:**
```json
{
  "id": "st-001",
  "name": "station-1",
  "display_name": "华东地区生产中心",
  "location": "江苏省苏州市",
  "phone": "0512-88888888",
  "manager": "李四",
  "manager_email": "lisi@company.com",
  "description": "主要负责华东地区的生产和维护",
  "is_active": true,
  "created_at": "2025-01-01T08:00:00Z",
  "updated_at": "2025-12-07T09:00:00Z"
}
```

---

### 2.3 备件表 (parts)

用途: 存储所有的备件信息和库存数据

| 字段名 | 数据类型 | 约束 | 说明 |
|------|---------|------|------|
| id | UUID/String | PRIMARY KEY | 备件唯一标识符 |
| name | VARCHAR(255) | NOT NULL | 备件名称 (如: "滤芯 A", "电池 B") |
| model | VARCHAR(100) | NOT NULL | 备件适用型号 (如: "XYZ-2000", "ABC-500") |
| description | TEXT | NULLABLE | 备件详细描述 |
| location | VARCHAR(255) | NULLABLE | 存放位置 (如: "A区第3排第2个柜") |
| supplier | VARCHAR(255) | NULLABLE | 供应商名称 |
| supplier_code | VARCHAR(100) | NULLABLE | 供应商备件编号 |
| qty | INT | NOT NULL, DEFAULT 0, CHECK (qty >= 0) | 当前库存数量 |
| alarmQty | INT | NOT NULL, DEFAULT 1 | 告警阈值（当库存 <= 此值时告警） |
| procurementDays | INT | NULLABLE, CHECK (procurementDays > 0) | 采购周期（天） |
| cost | DECIMAL(10, 2) | NULLABLE | 单位成本价格 |
| retail_price | DECIMAL(10, 2) | NULLABLE | 零售价格 |
| imageUrl | VARCHAR(500) | NULLABLE | 备件图片 URL（存储服务器地址或 CDN URL） |
| stationId | UUID/String | NOT NULL, FK → stations(id) | 所属场站 |
| category | VARCHAR(100) | NULLABLE | 备件分类 (如: "液压", "电气", "机械") |
| status | ENUM('active', 'discontinued', 'archived') | NOT NULL, DEFAULT 'active' | 备件状态 |
| created_by | UUID/String | NOT NULL, FK → users(id) | 创建人 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_by | UUID/String | NULLABLE, FK → users(id) | 最后修改人 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新时间 |
| last_purchase_date | DATETIME | NULLABLE | 最后采购日期 |
| last_use_date | DATETIME | NULLABLE | 最后使用日期 |

**索引:**
```sql
CREATE INDEX idx_parts_stationId ON parts(stationId);
CREATE INDEX idx_parts_name ON parts(name);
CREATE INDEX idx_parts_model ON parts(model);
CREATE INDEX idx_parts_status ON parts(status);
CREATE INDEX idx_parts_alarmStatus ON parts(qty, alarmQty);
CREATE INDEX idx_parts_created_at ON parts(created_at);
CREATE FULL_TEXT INDEX idx_parts_fulltext ON parts(name, model, description);
```

**示例数据:**
```json
{
  "id": "p-001",
  "name": "滤芯 A",
  "model": "XYZ-2000",
  "description": "用于 XYZ 系列机器的空气滤芯，需每月更换一次",
  "location": "A区第3排第2个柜",
  "supplier": "滤清器有限公司",
  "supplier_code": "SUP-12345",
  "qty": 10,
  "alarmQty": 3,
  "procurementDays": 7,
  "cost": 85.50,
  "retail_price": 120.00,
  "imageUrl": "https://cdn.company.com/images/parts/p-001.jpg",
  "stationId": "st-001",
  "category": "液压",
  "status": "active",
  "created_by": "u1",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_by": "u1",
  "updated_at": "2025-12-06T14:30:00Z",
  "last_purchase_date": "2025-12-01T09:00:00Z",
  "last_use_date": "2025-12-05T16:20:00Z"
}
```

---

### 2.4 库存变更日志表 (inventory_logs)

用途: 记录所有库存变化，用于审计和追踪

| 字段名 | 数据类型 | 约束 | 说明 |
|------|---------|------|------|
| id | UUID/String | PRIMARY KEY | 日志唯一标识符 |
| partId | UUID/String | NOT NULL, FK → parts(id) | 关联的备件 |
| operation | ENUM('create', 'update', 'in', 'out', 'adjust') | NOT NULL | 操作类型 |
| qty_before | INT | NULLABLE | 变更前数量 |
| qty_after | INT | NOT NULL | 变更后数量 |
| qty_change | INT | NOT NULL | 变更数量 (可为负) |
| reason | VARCHAR(255) | NOT NULL | 变更原因 (如: "采购入库", "领用出库", "盘点调整") |
| operator_id | UUID/String | NOT NULL, FK → users(id) | 操作人员 |
| notes | TEXT | NULLABLE | 备注信息 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**索引:**
```sql
CREATE INDEX idx_inventory_logs_partId ON inventory_logs(partId);
CREATE INDEX idx_inventory_logs_operator_id ON inventory_logs(operator_id);
CREATE INDEX idx_inventory_logs_created_at ON inventory_logs(created_at);
```

**示例数据:**
```json
{
  "id": "log-001",
  "partId": "p-001",
  "operation": "in",
  "qty_before": 8,
  "qty_after": 10,
  "qty_change": 2,
  "reason": "采购入库",
  "operator_id": "u1",
  "notes": "采购订单号: PO-2025-12-001",
  "created_at": "2025-12-07T10:00:00Z"
}
```

---

### 2.5 互通申请表 (transfer_requests) - 可选

用途: 记录场站间备件互通的申请和审批

| 字段名 | 数据类型 | 约束 | 说明 |
|------|---------|------|------|
| id | UUID/String | PRIMARY KEY | 申请唯一标识符 |
| partId | UUID/String | NOT NULL, FK → parts(id) | 申请的备件 |
| from_station | UUID/String | NOT NULL, FK → stations(id) | 来源场站 |
| to_station | UUID/String | NOT NULL, FK → stations(id) | 目标场站 |
| qty | INT | NOT NULL, CHECK (qty > 0) | 申请数量 |
| status | ENUM('pending', 'approved', 'rejected', 'completed', 'cancelled') | NOT NULL, DEFAULT 'pending' | 申请状态 |
| requester_id | UUID/String | NOT NULL, FK → users(id) | 申请人 |
| approver_id | UUID/String | NULLABLE, FK → users(id) | 审批人 |
| reason | TEXT | NULLABLE | 申请原因 |
| approval_notes | TEXT | NULLABLE | 审批意见 |
| transfer_date | DATETIME | NULLABLE | 互通日期 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**索引:**
```sql
CREATE INDEX idx_transfer_requests_partId ON transfer_requests(partId);
CREATE INDEX idx_transfer_requests_from_station ON transfer_requests(from_station);
CREATE INDEX idx_transfer_requests_to_station ON transfer_requests(to_station);
CREATE INDEX idx_transfer_requests_status ON transfer_requests(status);
```

---

## 3. 数据库关系和约束

### 3.1 外键关系

```sql
-- User 表
ALTER TABLE users ADD CONSTRAINT fk_users_stationId 
  FOREIGN KEY (stationId) REFERENCES stations(id) ON DELETE RESTRICT;

-- Part 表
ALTER TABLE parts ADD CONSTRAINT fk_parts_stationId 
  FOREIGN KEY (stationId) REFERENCES stations(id) ON DELETE RESTRICT;

ALTER TABLE parts ADD CONSTRAINT fk_parts_created_by 
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE parts ADD CONSTRAINT fk_parts_updated_by 
  FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL;

-- Inventory Logs 表
ALTER TABLE inventory_logs ADD CONSTRAINT fk_inventory_logs_partId 
  FOREIGN KEY (partId) REFERENCES parts(id) ON DELETE CASCADE;

ALTER TABLE inventory_logs ADD CONSTRAINT fk_inventory_logs_operator 
  FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE RESTRICT;

-- Transfer Requests 表 (可选)
ALTER TABLE transfer_requests ADD CONSTRAINT fk_transfer_requests_partId 
  FOREIGN KEY (partId) REFERENCES parts(id) ON DELETE CASCADE;

ALTER TABLE transfer_requests ADD CONSTRAINT fk_transfer_requests_from_station 
  FOREIGN KEY (from_station) REFERENCES stations(id) ON DELETE RESTRICT;

ALTER TABLE transfer_requests ADD CONSTRAINT fk_transfer_requests_to_station 
  FOREIGN KEY (to_station) REFERENCES stations(id) ON DELETE RESTRICT;

ALTER TABLE transfer_requests ADD CONSTRAINT fk_transfer_requests_requester 
  FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE RESTRICT;

ALTER TABLE transfer_requests ADD CONSTRAINT fk_transfer_requests_approver 
  FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE SET NULL;
```

---

## 4. 前端和后端的数据映射

### 4.1 前端 Part 类型 → 后端数据库

```typescript
// 前端 TypeScript 类型 (src/stores/parts.ts)
interface Part {
  id: string                  // ← parts.id
  name: string                // ← parts.name
  stationId: string           // ← parts.stationId
  qty: number                 // ← parts.qty
  model?: string              // ← parts.model
  location?: string           // ← parts.location
  alarmQty?: number           // ← parts.alarmQty
  procurementDays?: number    // ← parts.procurementDays
  desc?: string               // ← parts.description
  imageUrl?: string           // ← parts.imageUrl
}

// 后端扩展字段（不返回给前端或可选返回）
// - supplier: 供应商
// - cost: 成本价
// - status: 备件状态
// - created_by: 创建人
// - created_at: 创建时间
// - updated_at: 更新时间
// - last_purchase_date: 最后采购日期
```

### 4.2 API 请求/响应示例

**获取列表:**
```
GET /api/parts?stationId=station-1&status=active

Response (200):
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "p-001",
      "name": "滤芯 A",
      "model": "XYZ-2000",
      "qty": 10,
      "alarmQty": 3,
      "location": "A区3排2柜",
      "procurementDays": 7,
      "stationId": "station-1",
      "imageUrl": "https://...",
      "desc": "...",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-12-06T14:30:00Z"
    }
  ]
}
```

**创建备件:**
```
POST /api/parts

Request:
{
  "name": "新备件",
  "model": "ABC-123",
  "qty": 5,
  "alarmQty": 2,
  "location": "B区1排1柜",
  "procurementDays": 10,
  "stationId": "station-1",
  "description": "备件描述",
  "imageUrl": "data:image/jpeg;base64,..."  // Base64 编码的图片数据
}

Response (201):
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "p-new-001",
    "name": "新备件",
    ...
    "created_at": "2025-12-07T10:30:00Z"
  }
}
```

**更新备件:**
```
PUT /api/parts/:id

Request:
{
  "qty": 8,
  "alarmQty": 2,
  "location": "A区1排3柜"
  // 可部分更新
}

Response (200):
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "p-001",
    "qty": 8,
    ...
    "updated_at": "2025-12-07T10:45:00Z"
  }
}
```

---

## 5. 数据库初始化脚本

### 5.1 PostgreSQL 完整建表语句

```sql
-- 创建 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建 stations 表
CREATE TABLE stations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL UNIQUE,
  display_name VARCHAR(255) NOT NULL,
  location VARCHAR(255),
  phone VARCHAR(20),
  manager VARCHAR(100),
  manager_email VARCHAR(255),
  description TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_stations_name ON stations(name);
CREATE INDEX idx_stations_is_active ON stations(is_active);

-- 创建 users 表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  stationId UUID NOT NULL REFERENCES stations(id) ON DELETE RESTRICT,
  role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  is_active BOOLEAN NOT NULL DEFAULT true,
  last_login TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stationId ON users(stationId);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 创建 parts 表
CREATE TABLE parts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  model VARCHAR(100) NOT NULL,
  description TEXT,
  location VARCHAR(255),
  supplier VARCHAR(255),
  supplier_code VARCHAR(100),
  qty INTEGER NOT NULL DEFAULT 0 CHECK (qty >= 0),
  alarmQty INTEGER NOT NULL DEFAULT 1,
  procurementDays INTEGER CHECK (procurementDays > 0),
  cost DECIMAL(10, 2),
  retail_price DECIMAL(10, 2),
  imageUrl VARCHAR(500),
  stationId UUID NOT NULL REFERENCES stations(id) ON DELETE RESTRICT,
  category VARCHAR(100),
  status VARCHAR(50) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'discontinued', 'archived')),
  created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_purchase_date TIMESTAMP,
  last_use_date TIMESTAMP
);

CREATE INDEX idx_parts_stationId ON parts(stationId);
CREATE INDEX idx_parts_name ON parts(name);
CREATE INDEX idx_parts_model ON parts(model);
CREATE INDEX idx_parts_status ON parts(status);
CREATE INDEX idx_parts_alarmStatus ON parts(qty, alarmQty);
CREATE INDEX idx_parts_created_at ON parts(created_at);

-- 创建 inventory_logs 表
CREATE TABLE inventory_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  partId UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  operation VARCHAR(50) NOT NULL CHECK (operation IN ('create', 'update', 'in', 'out', 'adjust')),
  qty_before INTEGER,
  qty_after INTEGER NOT NULL,
  qty_change INTEGER NOT NULL,
  reason VARCHAR(255) NOT NULL,
  operator_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_logs_partId ON inventory_logs(partId);
CREATE INDEX idx_inventory_logs_operator_id ON inventory_logs(operator_id);
CREATE INDEX idx_inventory_logs_created_at ON inventory_logs(created_at);

-- 创建 transfer_requests 表 (可选)
CREATE TABLE transfer_requests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  partId UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
  from_station UUID NOT NULL REFERENCES stations(id) ON DELETE RESTRICT,
  to_station UUID NOT NULL REFERENCES stations(id) ON DELETE RESTRICT,
  qty INTEGER NOT NULL CHECK (qty > 0),
  status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'completed', 'cancelled')),
  requester_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  approver_id UUID REFERENCES users(id) ON DELETE SET NULL,
  reason TEXT,
  approval_notes TEXT,
  transfer_date TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transfer_requests_partId ON transfer_requests(partId);
CREATE INDEX idx_transfer_requests_from_station ON transfer_requests(from_station);
CREATE INDEX idx_transfer_requests_to_station ON transfer_requests(to_station);
CREATE INDEX idx_transfer_requests_status ON transfer_requests(status);
```

### 5.2 示例数据插入

```sql
-- 插入场站
INSERT INTO stations (name, display_name, location, phone, manager, manager_email, description)
VALUES 
  ('station-1', '华东地区生产中心', '江苏省苏州市', '0512-88888888', '李四', 'lisi@company.com', '主要负责华东地区的生产和维护'),
  ('station-2', '华南地区维修中心', '广东省深圳市', '0755-99999999', '王五', 'wangwu@company.com', '主要负责华南地区的维修和保养');

-- 插入用户
INSERT INTO users (name, email, password, stationId, role)
VALUES 
  ('张三', 'zhangsan@company.com', '$2b$10$...hashed_password...', (SELECT id FROM stations WHERE name='station-1'), 'user'),
  ('李四', 'lisi@company.com', '$2b$10$...hashed_password...', (SELECT id FROM stations WHERE name='station-1'), 'admin'),
  ('王五', 'wangwu@company.com', '$2b$10$...hashed_password...', (SELECT id FROM stations WHERE name='station-2'), 'user');

-- 插入备件
INSERT INTO parts (name, model, location, qty, alarmQty, procurementDays, stationId, category, description, created_by)
VALUES 
  ('滤芯 A', 'XYZ-2000', 'A区第3排第2个柜', 10, 3, 7, (SELECT id FROM stations WHERE name='station-1'), '液压', '用于 XYZ 系列机器的空气滤芯', (SELECT id FROM users WHERE email='zhangsan@company.com')),
  ('电池 B', 'ABC-500', 'B区第1排第5个柜', 5, 2, 14, (SELECT id FROM stations WHERE name='station-2'), '电气', '备用电源电池', (SELECT id FROM users WHERE email='wangwu@company.com')),
  ('螺丝 C', 'M8-100', 'C区第2排柜', 200, 50, 3, (SELECT id FROM stations WHERE name='station-1'), '机械', '标准螺丝', (SELECT id FROM users WHERE email='zhangsan@company.com'));
```

---

## 6. 字段说明补充

### 6.1 关键字段的业务含义

| 字段 | 说明 | 示例 |
|------|------|------|
| `alarmQty` | 告警阈值：当 `qty <= alarmQty` 时触发告警 | qty=10, alarmQty=3 → 显示红色告警 |
| `procurementDays` | 从下单到收货的天数，用于计算提前采购时间 | procurementDays=7，今天下单，7天后到货 |
| `imageUrl` | 可以是相对路径、绝对 URL 或 Base64 编码的图片数据 | `"https://cdn.company.com/parts/p-001.jpg"` 或 `"data:image/jpeg;base64,..."` |
| `status` | 备件状态，控制是否显示在列表中 | `active`: 正常; `discontinued`: 已停产; `archived`: 已归档 |
| `created_by` / `updated_by` | 操作审计，记录是谁创建/修改的备件 | 用于追踪数据变更责任 |

### 6.2 告警计算逻辑

```typescript
// 前端告警判断
function getAlarmStatus(qty: number, alarmQty: number) {
  if (alarmQty && qty <= alarmQty) {
    return 'alert';  // 显示红色告警
  }
  return 'normal';  // 正常状态
}

// 示例
// qty=10, alarmQty=3: 10 > 3 → normal (正常)
// qty=3, alarmQty=3: 3 <= 3 → alert (告警)
// qty=2, alarmQty=3: 2 <= 3 → alert (告警)
// qty=0, alarmQty=3: 0 <= 3 → alert (告警)
```

### 6.3 图片存储方案

**方案 A: Base64 编码 (当前前端实现)**
- 优点: 不需要单独的文件服务器，简单快速
- 缺点: 数据库体积大，性能差，难以版本管理
- 应用场景: MVP 和演示阶段

**方案 B: 文件上传到服务器 (推荐生产)**
```
1. 用户在表单中选择图片 → FormData
2. 前端 POST 到 /api/parts/:id/image → 返回文件路径
3. 后端保存文件到磁盘/CDN，返回访问 URL
4. 前端保存 URL 到 imageUrl 字段
5. 下次访问从 URL 加载图片 (快速，可缓存)
```

**方案 C: 云存储 (AWS S3, 阿里 OSS 等)**
- 优点: 自动备份，全球加速，容量无限
- 缺点: 需要费用，网络依赖
- 应用场景: 大规模生产环境

---

## 7. 性能优化建议

### 7.1 索引策略

```sql
-- 常用查询索引
CREATE INDEX idx_parts_station_status ON parts(stationId, status);
CREATE INDEX idx_parts_alarm ON parts(qty, alarmQty) WHERE status='active';

-- 统计查询索引
CREATE INDEX idx_inventory_logs_part_date ON inventory_logs(partId, created_at);

-- 搜索索引 (可选，需要全文搜索引擎)
-- PostgreSQL 全文搜索
CREATE INDEX idx_parts_search ON parts USING gin(
  to_tsvector('chinese', name || ' ' || model || ' ' || COALESCE(description, ''))
);
```

### 7.2 查询优化示例

```sql
-- ❌ 慢查询: 无索引，全表扫描
SELECT * FROM parts WHERE stationId = '...' AND status = 'active' AND qty <= alarmQty;

-- ✅ 快查询: 使用组合索引
CREATE INDEX idx_parts_station_status_alarm 
  ON parts(stationId, status) 
  WHERE qty <= alarmQty;

-- ✅ 分页查询
SELECT * FROM parts 
WHERE stationId = '...' AND status = 'active'
ORDER BY 
  CASE WHEN qty <= alarmQty THEN 0 ELSE 1 END,
  created_at DESC
LIMIT 20 OFFSET 0;
```

### 7.3 数据库连接池配置

```javascript
// Node.js 后端 (例如 Express + pg)
const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  max: 20,  // 最大连接数
  idleTimeoutMillis: 30000,  // 空闲超时
  connectionTimeoutMillis: 2000  // 连接超时
});
```

---

## 8. 数据库备份和恢复

### 8.1 PostgreSQL 备份

```bash
# 完整备份
pg_dump -U username -h localhost -d database_name > backup.sql

# 压缩备份
pg_dump -U username -h localhost -d database_name | gzip > backup.sql.gz

# 恢复
psql -U username -h localhost -d database_name < backup.sql
gunzip < backup.sql.gz | psql -U username -h localhost -d database_name
```

### 8.2 定期备份计划

```bash
# crontab 每日凌晨 2 点备份
0 2 * * * pg_dump -U username -d database_name | gzip > /backup/db_$(date +\%Y\%m\%d).sql.gz
```

---

## 9. 安全考虑

### 9.1 SQL 注入防护
- ✅ 使用 ORM (如 Sequelize, TypeORM) 或参数化查询
- ❌ 避免字符串拼接 SQL

### 9.2 密码存储
- ✅ 使用 bcrypt 进行哈希 (最少 10 rounds)
- ❌ 避免明文存储或简单加密

### 9.3 权限验证
- ✅ 后端必须验证 `user.stationId == part.stationId` 再执行更新
- ❌ 仅依赖前端验证

### 9.4 敏感数据
- password: 绝不返回给前端
- cost: 可选返回给管理员，不返回给普通用户

---

## 10. 技术栈建议

### 10.1 推荐配置

| 组件 | 推荐 | 原因 |
|------|------|------|
| 数据库 | PostgreSQL 13+ | 开源，稳定，支持 UUID，性能好 |
| ORM | TypeORM 或 Sequelize | 类型安全，迁移管理 |
| API 框架 | Express.js 或 Fastify | 轻量，生态好 |
| 认证 | JWT + bcrypt | 无状态，安全 |
| 文件存储 | 本地磁盘 + CDN 或 S3 | 灵活可扩展 |
| 日志 | Winston 或 Bunyan | 结构化日志，便于分析 |
| 监控 | Prometheus + Grafana | 性能监控和告警 |

### 10.2 数据库迁移工具

```bash
# 使用 Sequelize 管理迁移
npm install sequelize-cli

# 生成迁移文件
npx sequelize-cli migration:generate --name create-users-table

# 执行迁移
npx sequelize-cli db:migrate

# 回滚迁移
npx sequelize-cli db:migrate:undo
```

---

## 11. 后续扩展建议

### 短期 (1-3 个月)
- [ ] 图片上传服务
- [ ] 库存变更日志记录
- [ ] 数据导出功能 (CSV/Excel)

### 中期 (3-6 个月)
- [ ] 备件互通系统
- [ ] 采购管理功能
- [ ] 智能告警和提醒
- [ ] 权限分级管理

### 长期 (6-12 个月)
- [ ] 大数据分析
- [ ] 备件需求预测 (ML)
- [ ] 供应商管理系统
- [ ] 移动端 App

